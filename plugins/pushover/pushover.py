
import requests
import time
import pytz

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'
PUSHOVER_TOKEN = 'INSERT_API_TOKEN_HERE'
PUSHOVER_USER = 'INSERT_USER_KEY_HERE'
DASHBOARD_URL = 'http://try.alerta.io'

PUSHOVER_EMERG = 2  # requires user ack
PUSHOVER_HIGH = 1
PUSHOVER_NORMAL = 0
PUSHOVER_LOW = -1
PUSHOVER_BADGE = -2  # no notification

# See https://pushover.net/api#priority
PRIORITY_MAP = {
    'critical': PUSHOVER_EMERG,
    'major':    PUSHOVER_HIGH,
    'minor':    PUSHOVER_NORMAL,
    'warning':  PUSHOVER_LOW
}


class PushMessage(PluginBase):

    def pre_receive(self, alert):

        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        title = "%s: %s alert for %s - %s is %s" % (
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )

        priority = PRIORITY_MAP.get(alert.severity, PUSHOVER_BADGE)

        payload = {
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "title": title,
            "message": alert.text,
            "url": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
            "url_title": "View alert",
            "priority": priority,
            "timestamp": int(alert.get_date('create_time', fmt='epoch')),
            "sound": "tugboat"
        }

        if priority == PUSHOVER_EMERG:
            payload['retry'] = 299  # retry every seconds
            payload['expire'] = 900  # stop after seconds

        LOG.debug('Pushover.net payload: %s', payload)

        try:
            r = requests.post(PUSHOVER_URL, data=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("Pushover.net connection error: %s" % e)

        LOG.debug('Pushover.net response: %s - %s', r.status_code, r.text)

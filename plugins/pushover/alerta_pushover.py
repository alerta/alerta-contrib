
import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.pushover')

PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'

PUSHOVER_TOKEN = os.environ.get('PUSHOVER_TOKEN') or app.config['PUSHOVER_TOKEN']
PUSHOVER_USER = os.environ.get('PUSHOVER_USER') or app.config['PUSHOVER_USER']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

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
            "timestamp": alert.create_time,
            "sound": "tugboat"
        }

        if priority == PUSHOVER_EMERG:
            payload['retry'] = 299  # retry every seconds
            payload['expire'] = 900  # stop after seconds

        LOG.debug('Pushover.net: %s', payload)

        try:
            r = requests.post(PUSHOVER_URL, data=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("Pushover.net: ERROR - %s" % e)

        LOG.debug('Pushover.net: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):
        return

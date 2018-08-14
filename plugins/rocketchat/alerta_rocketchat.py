
import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.rocketchat')

ROCKETCHAT_WEBHOOK_URL = os.environ.get('ROCKETCHAT_WEBHOOK_URL') or app.config['ROCKETCHAT_WEBHOOK_URL']
ROCKETCHAT_CHANNEL = os.environ.get('ROCKETCHAT_CHANNEL') or app.config.get('ROCKETCHAT_CHANNEL', '')
ALERTA_USERNAME = os.environ.get('ALERTA_USERNAME') or app.config.get('ALERTA_USERNAME', 'alerta')
ICON_EMOJI = os.environ.get('ICON_EMOJI') or app.config.get('ICON_EMOJI', ':rocket:')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

DEFAULT_SEVERITY_MAP = {
    'security': '#000000',  # black
    'critical': '#FF0000',  # red
    'major': '#FFA500',  # orange
    'minor': '#FFFF00',  # yellow
    'warning': '#1E90FF',  #blue
    'informational': '#808080',  #gray
    'debug': '#808080',  # gray
    'trace': '#808080',  # gray
    'ok': '#00CC00'  # green
}


class PostMessage(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if alert.repeat:
            return
        self._post_message(self._prepare_payload(alert))

    def status_change(self, alert, status, text):
        if status not in ['ack', 'assign']:
            return
        self._post_message(self._prepare_payload(alert, status, text))

    @staticmethod
    def _prepare_payload(alert, status=None, text=None):
        title = '[{status}] {environment}: {event} on {resource}'.format(
            status=(status if status else alert.status).capitalize(),
            environment=alert.environment,
            severity=alert.severity,
            event=alert.event,
            resource=alert.resource
        )

        return {
            "channel": ROCKETCHAT_CHANNEL,
            "text": text,
            "alias": ALERTA_USERNAME,
            "emoji": ICON_EMOJI,
            "attachments": [{
                "title": title,
                "title_link": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
                "text": alert.text,
                "color": DEFAULT_SEVERITY_MAP.get(alert.severity, DEFAULT_SEVERITY_MAP['ok']),
                "fields": [
                        {"title": "Status", "value": (status if status else alert.status).capitalize(), "short": True},
                        {"title": "Environment", "value": alert.environment, "short": True},
                        {"title": "Resource", "value": alert.resource, "short": True},
                        {"title": "Services", "value": ", ".join(alert.service), "short": True}
                    ]
            }]
        }

    @staticmethod
    def _post_message(payload):
        LOG.debug('Rocket.Chat: %s', payload)

        try:
            r = requests.post(ROCKETCHAT_WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("Rocket.Chat: ERROR - %s" % e)

        LOG.debug('Rocket.Chat: %s - %s', r.status_code, r.text)

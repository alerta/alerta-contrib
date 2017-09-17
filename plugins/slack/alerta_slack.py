
import json
import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.slack')

SLACK_WEBHOOK_URL = os.environ.get(
    'SLACK_WEBHOOK_URL') or app.config['SLACK_WEBHOOK_URL']
SLACK_ATTACHMENTS = True if os.environ.get(
    'SLACK_ATTACHMENTS', 'False') == 'True' else app.config.get('SLACK_ATTACHMENTS', False)
SLACK_CHANNEL = os.environ.get(
    'SLACK_CHANNEL') or app.config.get('SLACK_CHANNEL', '')
SLACK_CHANNEL_ENV_MAP = os.environ.get(
    'SLACK_CHANNEL_ENV_MAP') or app.config.get('SLACK_CHANNEL_ENV_MAP', dict())
ALERTA_USERNAME = os.environ.get(
    'ALERTA_USERNAME') or app.config.get('ALERTA_USERNAME', 'alerta')
SLACK_SEND_ON_ACK = os.environ.get(
    'SLACK_SEND_ON_ACK') or app.config.get('SLACK_SEND_ON_ACK', False)
SLACK_SEVERITY_MAP = app.config.get('SLACK_SEVERITY_MAP', {})
SLACK_DEFAULT_SEVERITY_MAP = {'security': '#000000', # black
                              'critical': '#FF0000', # red
                              'major': '#FFA500', # orange
                              'minor': '#FFFF00', # yellow
                              'warning': '#1E90FF', #blue
                              'informational': '#808080', #gray
                              'debug': '#808080', # gray
                              'trace': '#808080', # gray
                              'ok': '#00CC00'} # green

ICON_EMOJI = os.environ.get('ICON_EMOJI') or app.config.get(
    'ICON_EMOJI', ':rocket:')
DASHBOARD_URL = os.environ.get(
    'DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class ServiceIntegration(PluginBase):

    def __init__(self, name=None):
        # override user-defined severities
        self._severities = SLACK_DEFAULT_SEVERITY_MAP
        self._severities.update(SLACK_SEVERITY_MAP)

        super(ServiceIntegration, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def _slack_prepare_payload(self, alert, status=None, text=None):
        summary = "*[%s] %s %s - _%s on %s_* <%s/#/alert/%s|%s>" % (
            (status if status else alert.status).capitalize(), alert.environment, alert.severity.capitalize(
            ), alert.event, alert.resource, DASHBOARD_URL,
            alert.id, alert.get_id(short=True)
        )

        if alert.severity in self._severities:
            color = self._severities[alert.severity]
        else:
            color = '#00CC00'  # green

        channel = SLACK_CHANNEL_ENV_MAP.get(alert.environment, SLACK_CHANNEL)

        txt = "<%s/#/alert/%s|%s> %s - %s" % (DASHBOARD_URL, alert.get_id(
        ), alert.get_id(short=True), alert.event, text if text else alert.text)

        if not SLACK_ATTACHMENTS:
            payload = {
                "username": ALERTA_USERNAME,
                "channel": channel,
                "text": summary,
                "icon_emoji": ICON_EMOJI
            }
        else:
            payload = {
                "username": ALERTA_USERNAME,
                "channel": channel,
                "icon_emoji": ICON_EMOJI,
                "attachments": [{
                    "fallback": summary,
                    "color": color,
                    "pretext": txt,
                    "fields": [
                        {"title": "Status", "value": (status if status else alert.status).capitalize(),
                         "short": True},
                        {"title": "Environment",
                            "value": alert.environment, "short": True},
                        {"title": "Resource", "value": alert.resource, "short": True},
                        {"title": "Services", "value": ", ".join(
                            alert.service), "short": True}
                    ]
                }]
            }

        return payload

    def post_receive(self, alert):

        if alert.repeat:
            return

        payload = self._slack_prepare_payload(alert)

        LOG.debug('Slack payload: %s', payload)

        try:
            r = requests.post(SLACK_WEBHOOK_URL,
                              data=json.dumps(payload), timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s', r.status_code)

    def status_change(self, alert, status, text):
        if SLACK_SEND_ON_ACK == False or status not in ['ack', 'assign']:
            return

        payload = self._slack_prepare_payload(alert, status, text)

        LOG.debug('Slack payload: %s', payload)
        try:
            r = requests.post(SLACK_WEBHOOK_URL,
                              data=json.dumps(payload), timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s', r.status_code)

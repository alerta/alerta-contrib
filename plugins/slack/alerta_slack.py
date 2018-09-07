
import json
import logging
import os
import requests

try:
    from jinja2 import Template
except Exception as e:
    LOG.error('SLACK: ERROR - Jinja template error: %s, template functionality will be unavailable', e)

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
SLACK_SUMMARY_FMT = app.config.get('SLACK_SUMMARY_FMT', None)  # Message summary format
SLACK_DEFAULT_SUMMARY_FMT='*[{status}] {environment} {service} {severity}* - _{event} on {resource}_ <{dashboard}/#/alert/{alert_id}|{short_id}>'
ICON_EMOJI = os.environ.get('ICON_EMOJI') or app.config.get(
    'ICON_EMOJI', ':rocket:')
SLACK_PAYLOAD = app.config.get('SLACK_PAYLOAD', None)  # Full API control
DASHBOARD_URL = os.environ.get(
    'DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')
SLACK_HEADERS = {
    'Content-Type': 'application/json'
}
SLACK_TOKEN = os.environ.get('SLACK_TOKEN') or app.config['SLACK_TOKEN']
if SLACK_TOKEN:
    SLACK_HEADERS['Authorization'] = 'Bearer ' + SLACK_TOKEN

class ServiceIntegration(PluginBase):

    def __init__(self, name=None):
        # override user-defined severities
        self._severities = SLACK_DEFAULT_SEVERITY_MAP
        self._severities.update(SLACK_SEVERITY_MAP)

        super(ServiceIntegration, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def _format_template(self, templateFmt, templateVars):
        try:
            LOG.debug('SLACK: generating template: %s' % templateFmt)
            template = Template(templateFmt)
        except Exception as e:
            LOG.error('SLACK: ERROR - Template init failed: %s', e)
            return

        try:
            LOG.debug('SLACK: rendering template: %s' % templateFmt)
            LOG.debug('SLACK: rendering variables: %s' % templateVars)
            return template.render(**templateVars)
        except Exception as e:
            LOG.error('SLACK: ERROR - Template render failed: %s', e)
            return

    def _slack_prepare_payload(self, alert, status=None, text=None):

        if alert.severity in self._severities:
            color = self._severities[alert.severity]
        else:
            color = '#00CC00'  # green
        channel = SLACK_CHANNEL_ENV_MAP.get(alert.environment, SLACK_CHANNEL)
        templateVars = {
            'alert': alert,
            'status': status if status else alert.status,
            'config': app.config,
            'color': color,
            'channel': channel,
            'emoji': ICON_EMOJI,
        }

        if SLACK_PAYLOAD:
            LOG.info("Formatting with slack payload")
            payload = json.loads(self._format_template(json.dumps(SLACK_PAYLOAD), templateVars))
        else:
            if type(SLACK_SUMMARY_FMT) is str:
                summary = self._format_template(SLACK_SUMMARY_FMT, templateVars)
            else:
                summary = SLACK_DEFAULT_SUMMARY_FMT.format(
                    status=alert.status.capitalize(),
                    environment=alert.environment.upper(),
                    service=','.join(alert.service),
                    severity=alert.severity.capitalize(),
                    event=alert.event,
                    resource=alert.resource,
                    alert_id=alert.id,
                    short_id=alert.get_id(short=True),
                    dashboard=DASHBOARD_URL
                )
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
                    "text": summary,
                    "attachments": [{
                        "fallback": summary,
                        "color": color,
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
                              data=json.dumps(payload), headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

    def status_change(self, alert, status, text):
        if SLACK_SEND_ON_ACK == False or status not in ['ack', 'assign']:
            return

        payload = self._slack_prepare_payload(alert, status, text)

        LOG.debug('Slack payload: %s', payload)
        try:
            r = requests.post(SLACK_WEBHOOK_URL,
                              data=json.dumps(payload), headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

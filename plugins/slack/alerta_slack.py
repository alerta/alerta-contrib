import json
import logging
import os

import requests

LOG = logging.getLogger('alerta.plugins.slack')

try:
    from jinja2 import Template
except Exception as e:
    LOG.warning('Slack Jinja template error: %s, template functionality will be unavailable', e)

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL') or app.config['SLACK_WEBHOOK_URL']
SLACK_ATTACHMENTS = True if os.environ.get('SLACK_ATTACHMENTS', 'False') == 'True' else app.config.get(
    'SLACK_ATTACHMENTS', False)
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL') or app.config.get('SLACK_CHANNEL', '')
SLACK_CHANNEL_ENV_MAP = os.environ.get('SLACK_CHANNEL_ENV_MAP') or app.config.get('SLACK_CHANNEL_ENV_MAP', {})
ALERTA_USERNAME = os.environ.get('ALERTA_USERNAME') or app.config.get('ALERTA_USERNAME', 'alerta')

SLACK_SEND_ON_ACK = os.environ.get('SLACK_SEND_ON_ACK') or app.config.get('SLACK_SEND_ON_ACK', False)
SLACK_SEVERITY_MAP = app.config.get('SLACK_SEVERITY_MAP', {})
SLACK_DEFAULT_SEVERITY_MAP = {
    'security': '#000000',  # black
    'critical': '#FF0000',  # red
    'major': '#FFA500',  # orange
    'minor': '#FFFF00',  # yellow
    'warning': '#1E90FF',  # blue
    'informational': '#808080',  # gray
    'debug': '#808080',  # gray
    'trace': '#808080',  # gray
    'ok': '#00CC00'  # green
}

SLACK_SUMMARY_FMT = os.environ.get('SLACK_SUMMARY_FMT') or app.config.get('SLACK_SUMMARY_FMT',
                                                                          None)  # Message summary format
SLACK_DEFAULT_SUMMARY_FMT = '<b>[{status}] {environment} {service} {severity} - <i>{event} on {resource}</i></b> <a href="{dashboard}/#/alert/{alert_id}">{short_id}</a>'
SLACK_DEFAULT_ATTACHMENT_SIZE_MAP = {
    'resource': False,
    'severity': True,
    'environment': True,
    'status': True,
    'services': True
}
SLACK_ATTACHMENT_SIZE_MAP = app.config.get('SLACK_ATTACHMENT_SIZE_MAP', SLACK_DEFAULT_ATTACHMENT_SIZE_MAP)
ICON_EMOJI = os.environ.get('ICON_EMOJI') or app.config.get('ICON_EMOJI', ':rocket:')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

SLACK_HEADERS = {
    'Content-Type': 'application/json'
}
SLACK_TOKEN = os.environ.get('SLACK_TOKEN') or app.config.get('SLACK_TOKEN', None)
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

    def _slack_prepare_payload(self, alert, status=None, text=None):
        if SLACK_SUMMARY_FMT:
            try:
                LOG.debug('SLACK: generating template: %s' % SLACK_SUMMARY_FMT)
                template = Template(SLACK_SUMMARY_FMT)
            except Exception as e:
                LOG.error('SLACK: ERROR - Template init failed: %s', e)
                return

            try:
                LOG.debug('SLACK: rendering template: %s' % SLACK_SUMMARY_FMT)
                template_vars = {
                    'alert': alert,
                    'config': app.config
                }
                summary = template.render(**template_vars)
            except Exception as e:
                LOG.error('SLACK: ERROR - Template render failed: %s', e)
                return
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

        if alert.severity in self._severities:
            color = self._severities[alert.severity]
        else:
            color = '#00CC00'  # green

        channel = SLACK_CHANNEL_ENV_MAP.get(alert.environment, SLACK_CHANNEL)

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
                    "color": color,
                    "fields": [
                        {
                            "title": "Resource",
                            "value": alert.resource,
                            "short": SLACK_ATTACHMENT_SIZE_MAP['resource']
                        },
                        {
                            "title": "Severity",
                            "value": alert.severity.capitalize(),
                            "short": SLACK_ATTACHMENT_SIZE_MAP['severity']
                        },
                        {
                            "title": "Status",
                            "value": (status if status else alert.status).capitalize(),
                            "short": SLACK_ATTACHMENT_SIZE_MAP['status']
                        },
                        {
                            "title": "Environment",
                            "value": alert.environment,
                            "short": SLACK_ATTACHMENT_SIZE_MAP['environment']
                        },
                        {
                            "title": "Services",
                            "value": ", ".join(alert.service),
                            "short": SLACK_ATTACHMENT_SIZE_MAP['services']
                        }
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
            r = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

    def status_change(self, alert, status, text):
        if SLACK_SEND_ON_ACK == False or status not in ['ack', 'assign']:
            return

        payload = self._slack_prepare_payload(alert, status, text)
        LOG.debug('Slack payload: %s', payload)

        try:
            r = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

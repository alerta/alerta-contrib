
import json
import logging
import os
import requests
import traceback

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

SLACK_ATTACHMENTS = True if os.environ.get(
    'SLACK_ATTACHMENTS', 'False') == 'True' else app.config.get('SLACK_ATTACHMENTS', False)
try:
    SLACK_CHANNEL_ENV_MAP = json.loads(
        os.environ.get('SLACK_CHANNEL_ENV_MAP'))
except Exception as e:
    SLACK_CHANNEL_ENV_MAP = app.config.get('SLACK_CHANNEL_ENV_MAP', dict())

try:
    SLACK_CHANNEL_EVENT_MAP = json.loads(
        os.environ.get('SLACK_CHANNEL_EVENT_MAP'))
except Exception as e:
    SLACK_CHANNEL_EVENT_MAP = app.config.get('SLACK_CHANNEL_EVENT_MAP', dict())

try:
    SLACK_CHANNEL_SEVERITY_MAP = json.loads(
        os.environ.get('SLACK_CHANNEL_SEVERITY_MAP'))
except Exception as e:
    SLACK_CHANNEL_SEVERITY_MAP = app.config.get('SLACK_CHANNEL_SEVERITY_MAP', dict())
    
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
SLACK_DEFAULT_SUMMARY_FMT='*[{status}] {environment} {service} {severity}* - _{event} on {resource}_ <{dashboard}/#/alert/{alert_id}|{short_id}>'
SLACK_HEADERS = {
    'Content-Type': 'application/json'
}

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

    def _slack_prepare_payload(self, alert, status=None, text=None, **kwargs):
        SLACK_CHANNEL = self.get_config('SLACK_CHANNEL', default='', type=str, **kwargs)
        SLACK_SUMMARY_FMT = self.get_config('SLACK_SUMMARY_FMT', type=str, **kwargs)  # Message summary format
        SLACK_PAYLOAD = self.get_config('SLACK_PAYLOAD', type=str, **kwargs)  # Full API control
        ICON_EMOJI = self.get_config('ICON_EMOJI', default=':rocket:', type=str, **kwargs)
        ALERTA_USERNAME = self.get_config('ALERTA_USERNAME', default='alerta', type=str, **kwargs)
        DASHBOARD_URL = self.get_config('DASHBOARD_URL', default='', type=str, **kwargs)
        SLACK_TOKEN = self.get_config('SLACK_TOKEN', type=str, **kwargs)
        if SLACK_TOKEN:
            SLACK_HEADERS['Authorization'] = 'Bearer ' + SLACK_TOKEN

        if alert.severity in self._severities:
            color = self._severities[alert.severity]
        else:
            color = '#00CC00'  # green
        channel = SLACK_CHANNEL_SEVERITY_MAP.get(alert.severity, SLACK_CHANNEL)
        if SLACK_CHANNEL_SEVERITY_MAP.get(alert.severity):
            LOG.debug("Found severity mapping. Channel: %s" % channel)
        else:
            LOG.debug("No severity mapping. Channel: %s" % channel)
        channel = SLACK_CHANNEL_ENV_MAP.get(alert.environment, channel)
        if SLACK_CHANNEL_ENV_MAP.get(alert.environment):
            LOG.debug("Found env mapping. Channel: %s" % channel)
        else:
            LOG.debug("No env mapping. Channel: %s" % channel)
        channel = SLACK_CHANNEL_EVENT_MAP.get(alert.event, channel)
        if SLACK_CHANNEL_EVENT_MAP.get(alert.event):
            LOG.debug("Found event mapping. Channel: %s" % channel)
        else:
            LOG.debug("No event mapping. Channel: %s" % channel)

        templateVars = {
            'alert': alert,
            'status': status if status else alert.status,
            'config': app.config,
            'color': color,
            'channel': channel,
            'emoji': ICON_EMOJI,
        }

        if SLACK_PAYLOAD:
            LOG.debug("Formatting with slack payload template")
            formattedPayload = self._format_template(json.dumps(SLACK_PAYLOAD), templateVars).replace('\n', '\\n')
            LOG.debug("Formatted slack payload:\n%s" % formattedPayload)
            payload = json.loads(formattedPayload)
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

    def post_receive(self, alert, **kwargs):
        SLACK_WEBHOOK_URL = self.get_config('SLACK_WEBHOOK_URL', type=str, **kwargs)

        if alert.repeat:
            return

        try:
            payload = self._slack_prepare_payload(alert, **kwargs)

            LOG.debug('Slack payload: %s', payload)
        except Exception as e:
            LOG.error('Exception formatting payload: %s\n%s' % (e, traceback.format_exc()))
            return

        try:
            r = requests.post(SLACK_WEBHOOK_URL,
                              data=json.dumps(payload), headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

    def status_change(self, alert, status, text, **kwargs):
        SLACK_WEBHOOK_URL = self.get_config('SLACK_WEBHOOK_URL', type=str, **kwargs)

        if SLACK_SEND_ON_ACK == False or status not in ['ack', 'assign']:
            return

        try:
            payload = self._slack_prepare_payload(alert, status, text, **kwargs)

            LOG.debug('Slack payload: %s', payload)
        except Exception as e:
            LOG.error('Exception formatting payload: %s\n%s' % (e, traceback.format_exc()))
            return

        try:
            r = requests.post(SLACK_WEBHOOK_URL,
                              data=json.dumps(payload), headers=SLACK_HEADERS, timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s\n%s' % (r.status_code, r.text))

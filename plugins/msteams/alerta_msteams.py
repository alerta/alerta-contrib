
import json
import logging
import os
import requests
import pymsteams

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.msteams')

try:
    from jinja2 import Template
except Exception as e:
    LOG.error('MS Teams: ERROR - Jinja template error: %s, template functionality will be unavailable', e)

MS_TEAMS_COLORS_MAP = app.config.get('MS_TEAMS_COLORS_MAP', {})
MS_TEAMS_DEFAULT_COLORS_MAP = {'security': '000000',
                              'critical': 'D8122A',
                              'major': 'EA680F',
                              'minor': 'FFBE1E',
                              'warning': '1E90FF'}
MS_TEAMS_DEFAULT_COLOR = '00AA5A'
MS_TEAMS_DEFAULT_TIMEOUT = 7 # pymsteams http_timeout

class SendConnectorCardMessage(PluginBase):

    def __init__(self, name=None):
        # override user-defined severities(colors)
        self._colors = MS_TEAMS_DEFAULT_COLORS_MAP
        self._colors.update(MS_TEAMS_COLORS_MAP)

        super(SendConnectorCardMessage, self).__init__(name)

    def _load_template(self, templateFmt):
        try:
            if os.path.exists(templateFmt):
                with open(templateFmt, 'r') as f:
                    template = Template(f.read())
            else:
                template = Template(templateFmt)
            return template
        except Exception as e:
            LOG.error('MS Teams: ERROR - Template init failed: %s', e)
            return

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):
        MS_TEAMS_WEBHOOK_URL = self.get_config('MS_TEAMS_WEBHOOK_URL', default='', type=str, **kwargs)
        MS_TEAMS_SUMMARY_FMT = self.get_config('MS_TEAMS_SUMMARY_FMT', default=None, type=str, **kwargs)  # Message summary(title) format
        MS_TEAMS_TEXT_FMT = self.get_config('MS_TEAMS_TEXT_FMT', default=None, type=str, **kwargs)  # Message text format
        MS_TEAMS_PAYLOAD = self.get_config('MS_TEAMS_PAYLOAD', default=None, type=str, **kwargs)  # json/Jinja2 MS teams messagecard payload
        MS_TEAMS_INBOUNDWEBHOOK_URL = self.get_config('MS_TEAMS_INBOUNDWEBHOOK_URL', default=None, type=str, **kwargs)  # webhook url for connectorcard actions
        MS_TEAMS_APIKEY = self.get_config('MS_TEAMS_APIKEY', default=None, type=str, **kwargs)  # X-API-Key (needs webhook.write permission)
        DASHBOARD_URL = self.get_config('DASHBOARD_URL', default='', type=str, **kwargs)

        if alert.repeat:
            return

        color = self._colors.get(alert.severity, MS_TEAMS_DEFAULT_COLOR)
        url = "%s/#/alert/%s" % (DASHBOARD_URL, alert.id)

        template_vars = {
            'alert': alert,
            'config': app.config,
            'color': color,
            'url': url
        }

        if MS_TEAMS_INBOUNDWEBHOOK_URL and MS_TEAMS_APIKEY:
            # Add X-API-Key header for teams(webhook) HttpPOST actions
            template_vars['headers'] =  '[ {{ "name": "X-API-Key", "value": "{}" }} ]'.format(MS_TEAMS_APIKEY)
            template_vars['webhook_url'] = MS_TEAMS_INBOUNDWEBHOOK_URL

        if MS_TEAMS_PAYLOAD:
            # Use "raw" json ms teams message card format
            payload_template = self._load_template(MS_TEAMS_PAYLOAD)
            try:
                card_json = payload_template.render(**template_vars)
                LOG.debug('MS Teams payload(json): %s', card_json)
                # Try to check that we've valid json
                json.loads(card_json)
            except Exception as e:
                LOG.error('MS Teams: ERROR - Template(PAYLOAD) render failed: %s', e)
                return
        else:
            # Use pymsteams to format/construct message card
            if MS_TEAMS_SUMMARY_FMT:
                template = self._load_template(MS_TEAMS_SUMMARY_FMT)
                try:
                    summary = template.render(**template_vars)
                except Exception as e:
                    LOG.error('MS Teams: ERROR - Template render failed: %s', e)
                    return
            else:
                summary = ('<b>[{status}] {environment} {service} {severity} - <i>{event} on {resource}</i></b>').format(
                    status=alert.status.capitalize(),
                    environment=alert.environment.upper(),
                    service=','.join(alert.service),
                    severity=alert.severity.capitalize(),
                    event=alert.event,
                    resource=alert.resource
                )

            if MS_TEAMS_TEXT_FMT:
                txt_template = self._load_template(MS_TEAMS_TEXT_FMT)
                try:
                    text = txt_template.render(**template_vars)
                except Exception as e:
                    LOG.error('MS Teams: ERROR - Template(TEXT_FMT) render failed: %s', e)
                    return
            else:
                text = alert.text

            LOG.debug('MS Teams payload: %s', summary)

        try:
            if MS_TEAMS_PAYLOAD:
                # Use requests.post to send raw json message card
                LOG.debug("MS Teams sending(json payload) POST to %s", MS_TEAMS_WEBHOOK_URL)
                r = requests.post(MS_TEAMS_WEBHOOK_URL, data=card_json, timeout=MS_TEAMS_DEFAULT_TIMEOUT)
                LOG.debug('MS Teams response: %s / %s' % (r.status_code, r.text))
            else:
                # Use pymsteams to send card
                msTeamsMessage = pymsteams.connectorcard(hookurl=MS_TEAMS_WEBHOOK_URL, http_timeout=MS_TEAMS_DEFAULT_TIMEOUT)
                msTeamsMessage.title(summary)
                msTeamsMessage.text(text)
                msTeamsMessage.addLinkButton("Open in Alerta", url)
                msTeamsMessage.color(color)
                msTeamsMessage.send()
        except Exception as e:
            raise RuntimeError("MS Teams: ERROR - %s", e)

    def status_change(self, alert, status, text, **kwargs):
        return

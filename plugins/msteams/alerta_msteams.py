
import json
import logging
import os
import requests
import pymsteams
import re

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

REGEX_PREFIX = "=~"

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

        MS_TEAMS_ALERT_WEBHOOK_MAP = self.get_config("MS_TEAMS_ALERT_WEBHOOK_MAP", default=[], type=list, **kwargs)

        ms_teams_webhooks = self._get_ms_teams_webhooks(MS_TEAMS_ALERT_WEBHOOK_MAP, alert)

        if len(ms_teams_webhooks) <= 0 and not MS_TEAMS_WEBHOOK_URL:
            return alert

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
                if MS_TEAMS_WEBHOOK_URL:
                    LOG.debug("MS Teams sending(json payload) POST to %s", MS_TEAMS_WEBHOOK_URL)
                    r = requests.post(MS_TEAMS_WEBHOOK_URL, data=card_json, timeout=MS_TEAMS_DEFAULT_TIMEOUT)
                    LOG.debug('MS Teams response: %s / %s' % (r.status_code, r.text))
                if ms_teams_webhooks:
                    for webhook in ms_teams_webhooks:
                        LOG.debug("MS Teams sending(json payload) POST to %s", webhook)
                        r = requests.post(webhook, data=card_json, timeout=MS_TEAMS_DEFAULT_TIMEOUT)
                        LOG.debug('MS Teams response: %s / %s' % (r.status_code, r.text))
            else:
                # Use pymsteams to send card
                if MS_TEAMS_WEBHOOK_URL:
                    self._send_card(MS_TEAMS_WEBHOOK_URL, summary, text, url, color)
                if ms_teams_webhooks:
                    for webhook in ms_teams_webhooks:
                        self._send_card(webhook, summary, text, url, color)
        except Exception as e:
            raise RuntimeError("MS Teams: ERROR - %s", e)

    def _send_card(self, webhook_url, summary, text, url, color):
        LOG.debug("MS Teams sending(json payload) POST to %s", webhook_url)
        msTeamsMessage = pymsteams.connectorcard(hookurl=webhook_url, http_timeout=MS_TEAMS_DEFAULT_TIMEOUT)
        msTeamsMessage.title(summary)
        msTeamsMessage.text(text)
        msTeamsMessage.addLinkButton("Open in Alerta", url)
        msTeamsMessage.color(color)
        msTeamsMessage.send()

    def status_change(self, alert, status, text, **kwargs):
        return

    def _get_ms_teams_webhooks(self, webhook_mappings, alert):
        webhooks = list()
        for mapping in webhook_mappings:
            LOG.debug(mapping['attributes'])
            attributes_match = self._match_attributes(mapping, alert)
            if attributes_match:
                webhooks.append(mapping['ms_teams_webhook'])
        return webhooks

    def _match_attributes(self, mapping, alert):
        for k, v in mapping['attributes'].items():
            LOG.debug(f"{k} = {v}")
            if not hasattr(alert, k) and k not in alert.attributes:
                LOG.debug(f"Attribute {k} does not exist!")
                return False
            if v.startswith(REGEX_PREFIX):
                match = self._match_attribute_regex(alert, k, v)
                if not match:
                    return False
            else:
                match = self._match_attribute_str(alert, k, v)
                if not match:
                    return False
        return True
    
    def _match_attribute_regex(self, alert, attr_name, regex_pattern):
        # Check if attribute exists as default alerta variable, if not check if 
        # attribute is in custom defined attributes array of the alert
        pattern = self.remove_prefix(regex_pattern, REGEX_PREFIX)
        if hasattr(alert, attr_name):
            return re.fullmatch(pattern, getattr(attr_name))
        return re.fullmatch(pattern, alert.attributes.get(attr_name))

    def _match_attribute_str(self,alert, attr_name, attr_value):
        # Check if attribute exists as default alerta variable, if not check if 
        # attribute is in custom defined attributes array of the alert
        if hasattr(alert, attr_name) and getattr(alert, attr_name) == attr_value:
            return True
        return alert.attributes.get(attr_name) == attr_value
    
    def remove_prefix(self, text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text
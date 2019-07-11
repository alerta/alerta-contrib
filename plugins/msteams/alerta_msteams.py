
import json
import logging
import os
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
MS_TEAMS_DEFAULT_COLORS_MAP = {'critical': 'D8122A',
                              'major': 'EA680F',
                              'minor': 'FFBE1E',
                              'warning': 'BA2222'}
MS_TEAMS_DEFAULT_COLOR = '00AA5A'

class SendConnectorCardMessage(PluginBase):

    def __init__(self, name=None):
        # override user-defined severities(colors)
        self._colors = MS_TEAMS_DEFAULT_COLORS_MAP
        self._colors.update(MS_TEAMS_COLORS_MAP)

        super(SendConnectorCardMessage, self).__init__(name)

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):
        MS_TEAMS_WEBHOOK_URL = self.get_config('MS_TEAMS_WEBHOOK_URL', default='', type=str, **kwargs)
        MS_TEAMS_SUMMARY_FMT = self.get_config('MS_TEAMS_SUMMARY_FMT', default=None, type=str, **kwargs)  # Message summary(title) format
        MS_TEAMS_TEXT_FMT = self.get_config('MS_TEAMS_TEXT_FMT', default=None, type=str, **kwargs)  # Message text format
        DASHBOARD_URL = self.get_config('DASHBOARD_URL', default='', type=str, **kwargs)

        if alert.repeat:
            return

        if MS_TEAMS_SUMMARY_FMT:
            try:
                if os.path.exists(MS_TEAMS_SUMMARY_FMT):
                    with open(MS_TEAMS_SUMMARY_FMT, 'r') as f:
                        template = Template(f.read())
                else:
                    template = Template(MS_TEAMS_SUMMARY_FMT)
            except Exception as e:
                LOG.error('MS Teams: ERROR - Template init failed: %s', e)
                return

            try:
                template_vars = {
                    'alert': alert,
                    'config': app.config
                }
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

        url = "%s/#/alert/%s" % (DASHBOARD_URL, alert.id)

        if MS_TEAMS_TEXT_FMT:
            try:
                if os.path.exists(MS_TEAMS_TEXT_FMT):
                    with open(MS_TEAMS_TEXT_FMT, 'r') as f:
                        txt_template = Template(f.read())
                else:
                    txt_template = Template(MS_TEAMS_TEXT_FMT)
            except Exception as e:
                LOG.error('MS Teams: ERROR - Template(TEXT_FMT) init failed: %s', e)
                return
            try:
                template_vars = {
                    'alert': alert,
                    'config': app.config
                }
                text = txt_template.render(**template_vars)
            except Exception as e:
                LOG.error('MS Teams: ERROR - Template(TEXT_FMT) render failed: %s', e)
                return
        else:
            text = alert.text

        color = self._colors.get(alert.severity, MS_TEAMS_DEFAULT_COLOR)

        LOG.debug('MS Teams payload: %s', summary)

        try:
            msTeamsMessage = pymsteams.connectorcard(MS_TEAMS_WEBHOOK_URL)
            msTeamsMessage.title(summary)
            msTeamsMessage.text(text)
            msTeamsMessage.addLinkButton("Open in Alerta", url)
            msTeamsMessage.color(color)
            msTeamsMessage.send()
        except Exception as e:
            raise RuntimeError("MS Teams: ERROR - %s", e)

    def status_change(self, alert, status, text, **kwargs):
        return

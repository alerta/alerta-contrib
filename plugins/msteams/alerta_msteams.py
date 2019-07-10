
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

MS_TEAMS_WEBHOOK_URL = os.environ.get('MS_TEAMS_WEBHOOK_URL') or app.config.get('MS_TEAMS_WEBHOOK_URL')
MS_TEAMS_SUMMARY_FMT = os.environ.get('MS_TEAMS_SUMMARY_FMT') or app.config.get('MS_TEAMS_SUMMARY_FMT', None)  # Message summary(title) format
MS_TEAMS_TEXT_FMT = os.environ.get('MS_TEAMS_TEXT_FMT') or app.config.get('MS_TEAMS_TEXT_FMT', None)  # Message text format
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

try:
    from jinja2 import Template
except Exception as e:
    LOG.error('MS Teams: ERROR - Jinja template error: %s, template functionality will be unavailable', e)


class SendConnectorCardMessage(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

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

        if alert.severity == 'critical':
            color = "D8122A"
        elif alert.severity == 'major':
            color = "EA680F"
        elif alert.severity == 'minor':
            color = "FFBE1E"
        elif alert.severity == 'warning':
            color = "BA2222"
        else:
            color = "00AA5A"

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

    def status_change(self, alert, status, text):
        return


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

MS_TEAMS_URL = os.environ.get('MS_TEAMS_WEBHOOK') or app.config.get('MS_TEAMS_WEBHOOK')
MS_TEAMS_SUMMARY_FMT = os.environ.get('MS_TEAMS_SUMMARY_FMT') or app.config.get('MS_TEAMS_SUMMARY_FMT', None)  # Message summary format
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
            summary = ('<b>[{status}] {environment} {service} {severity} - <i>{event} on {resource}</i></b> <a href="{dashboard}/#/alert/{alert_id}">{short_id}</a>').format(
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
            url = "%s/#/alert/%s" % (DASHBOARD_URL, alert.id)

        LOG.debug('MS Teams payload: %s', summary)

        try:
            msTeamsMessage = pymsteams.connectorcard(MS_TEAMS_URL)
            msTeamsMessage.text(summary)
            msTeamsMessage.addLinkButton("Open in Alerta", url)
            msTeamsMessage.send()
        except Exception as e:
            raise RuntimeError("MS Teams: ERROR - %s", e)

    def status_change(self, alert, status, text):
        return

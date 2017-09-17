
import json
import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.hipchat')

HIPCHAT_URL = os.environ.get('HIPCHAT_URL') or app.config.get('HIPCHAT_URL', 'https://api.hipchat.com/v2') # Hipchat URL, change if using privately hosted Hipchat
HIPCHAT_ROOM = os.environ.get('HIPCHAT_ROOM') or app.config['HIPCHAT_ROOM']  # Room Name or Room API ID
HIPCHAT_API_KEY = os.environ.get('HIPCHAT_API_KEY') or app.config['HIPCHAT_API_KEY']  # Room Notification Token
HIPCHAT_SUMMARY_FMT = os.environ.get('HIPCHAT_SUMMARY_FMT') or app.config.get('HIPCHAT_SUMMARY_FMT', None)  # Message summary format
HIPCHAT_VERIFY_SSL = os.environ.get('HIPCHAT_VERIFY_SSL') or app.config.get('HIPCHAT_VERIFY_SSL', True) # Verify SSL cert from Hipchat
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

try:
    from jinja2 import Template
except Exception as e:
    LOG.error('HipChat: ERROR - Jinja template error: %s, template functionality will be unavailable', e)


class SendRoomNotification(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        if HIPCHAT_SUMMARY_FMT:
            try:
                template = Template(HIPCHAT_SUMMARY_FMT)
            except Exception as e:
                LOG.error('HipChat: ERROR - Template init failed: %s', e)
                return

            try:
                template_vars = {
                    'alert': alert,
                    'config': app.config
                }
                summary = template.render(**template_vars)
            except Exception as e:
                LOG.error('HipChat: ERROR - Template render failed: %s', e)
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

        if alert.severity == 'critical':
            color = "red"
        elif alert.severity == 'major':
            color = "purple"
        elif alert.severity == 'minor':
            color = "yellow"
        elif alert.severity == 'warning':
            color = "gray"
        else:
            color = "green"

        payload = {
            "color": color,
            "message": summary,
            "notify": True,
            "message_format": "html"
        }
        LOG.debug('HipChat payload: %s', payload)

        url = '%s/room/%s/notification' % (HIPCHAT_URL, HIPCHAT_ROOM)
        headers = {
            'Authorization': 'Bearer ' + HIPCHAT_API_KEY,
            'Content-type': 'application/json'
        }

        LOG.debug('HipChat: Notification sent to %s', url)
        try:
            r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=2, verify=HIPCHAT_VERIFY_SSL)
        except Exception as e:
            raise RuntimeError("HipChat: ERROR - %s", e)

        LOG.debug('HipChat: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):
        return

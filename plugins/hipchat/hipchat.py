
import os
import json
import requests

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

HIPCHAT_URL = 'https://api.hipchat.com/v2'
HIPCHAT_ROOM = os.environ.get('HIPCHAT_ROOM') or app.config['HIPCHAT_ROOM']  # Room Name or Room API ID
HIPCHAT_API_KEY = os.environ.get('HIPCHAT_API_KEY') or app.config['HIPCHAT_API_KEY']  # Room Notification Token

HIPCHAT_SUMMARY_TEMPLATE = None
HIPCHAT_SUMMARY_FMT = os.environ.get('HIPCHAT_SUMMARY_FMT') or app.config.get('HIPCHAT_SUMMARY_FMT', None)  # Message summary format
if HIPCHAT_SUMMARY_FMT:
    try:
        from jinja2 import Template
        HIPCHAT_SUMMARY_TEMPLATE = Template(HIPCHAT_SUMMARY_FMT)
    except Exception as e:
        LOG.error('Jinja template error: {}, template functionality will be unavailable'.format(e))

class SendRoomNotification(PluginBase):

    def pre_receive(self, alert):

        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        url = '%s/room/%s/notification' % (HIPCHAT_URL, HIPCHAT_ROOM)

        summary = None
        if HIPCHAT_SUMMARY_TEMPLATE:
            try:
                template_vars = {
                    'alert': alert,
                    'config': app.config
                }
                summary = HIPCHAT_SUMMARY_TEMPLATE.render(**template_vars)
            except Exception as e:
                LOG.error('Summary template rendering error: {}'.format(e))

        if not summary:
            summary = "<b>[%s] %s %s - <i>%s on %s</i></b> <a href=\"http://try.alerta.io/#/alert/%s\">%s</a>" % (
                alert.status.capitalize(), alert.environment, alert.severity.capitalize(), alert.event, alert.resource,
                alert.id, alert.get_id(short=True)
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

        headers = {
            'Authorization': 'Bearer ' + HIPCHAT_API_KEY,
            'Content-type': 'application/json'
        }

        LOG.debug('HipChat sending notification to %s', url)
        try:
            r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=2)
        except Exception as e:
            raise RuntimeError("HipChat connection error: %s", e)

        LOG.debug('HipChat response: %s - %s', r.status_code, r.text)

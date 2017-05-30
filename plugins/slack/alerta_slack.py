
import os
import json
import requests
import logging

from alerta.app import app
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.slack')

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL') or app.config['SLACK_WEBHOOK_URL']
SLACK_ATTACHMENTS = True if os.environ.get('SLACK_ATTACHMENTS', 'False') == 'True' else app.config.get('SLACK_ATTACHMENTS', False)
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL') or app.config.get('SLACK_CHANNEL', '')
ALERTA_USERNAME = os.environ.get('ALERTA_USERNAME') or app.config.get('ALERTA_USERNAME', 'alerta')

ICON_EMOJI = os.environ.get('ICON_EMOJI') or app.config.get('ICON_EMOJI', ':rocket:')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')

class ServiceIntegration(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        url = SLACK_WEBHOOK_URL

        summary = "*[%s] %s %s - _%s on %s_* <%s/#/alert/%s|%s>" % (
            alert.status.capitalize(), alert.environment, alert.severity.capitalize(), alert.event, alert.resource, DASHBOARD_URL,
            alert.id, alert.get_id(short=True)
        )

        if alert.severity == 'security':
            color = "#000000"  # black
        if alert.severity == 'critical':
            color = "#FF0000"  # red
        elif alert.severity == 'major':
            color = "#FFA500"  # orange
        elif alert.severity == 'minor':
            color = "#FFFF00"  # yellow
        elif alert.severity == 'warning':
            color = "#1E90FF"  # blue
        elif alert.severity == 'information':
            color = "#808080"  # gray
        elif alert.severity == 'debug':
            color = "#808080"  # gray
        elif alert.severity == 'trace':
            color = "#808080"  # gray
        else:
            color = "#00CC00"  # green

        text = "<%s/#/alert/%s|%s> %s - %s" % (DASHBOARD_URL, alert.get_id(), alert.get_id(short=True), alert.event, alert.text)

        if not SLACK_ATTACHMENTS:

            payload = {
                "username": ALERTA_USERNAME,
                "channel": SLACK_CHANNEL,
                "text": summary,
                "icon_emoji": ICON_EMOJI
            }

        else:
            payload = {
                "username": ALERTA_USERNAME,
                "channel": SLACK_CHANNEL,
                "icon_emoji": ICON_EMOJI,
                "attachments": [{
                    "fallback": summary,
                    "color": color,
                    "pretext": text,
                    "fields": [
                        {"title": "Status", "value": alert.status.capitalize(), "short": True},
                        {"title": "Environment", "value": alert.environment, "short": True},
                        {"title": "Resource", "value": alert.resource, "short": True},
                        {"title": "Services", "value": ", ".join(alert.service), "short": True}
                    ]
                }]
            }

        LOG.debug('Slack payload: %s', payload)

        try:
            r = requests.post(url, data=json.dumps(payload), timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s', r.status_code)

    def status_change(self, alert, status, text):
        return

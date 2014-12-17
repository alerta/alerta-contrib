
import json
import requests

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/INSERT/YOUR/KEY'
SLACK_ATTACHMENTS = True


class ServiceIntegration(PluginBase):

    def pre_receive(self, alert):

        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        url = SLACK_WEBHOOK_URL

        summary = "*[%s] %s %s - _%s on %s_* <http://try.alerta.io/#/alert/%s|%s>" % (
            alert.status.capitalize(), alert.environment, alert.severity.capitalize(), alert.event, alert.resource,
            alert.id, alert.get_id(short=True)
        )

        if alert.severity == 'critical':
            color = "#FF0000"
        elif alert.severity == 'major':
            color = "#FFA500"
        elif alert.severity == 'minor':
            color = "#FFFF00"
        elif alert.severity == 'warning':
            color = "#1E90FF"  # blue
        else:
            color = "#00CC00"  # green

        text = "<http://try.alerta.io/#/alert/%s|%s> %s" % (alert.get_id(), alert.get_id(short=True), alert.text)

        if not SLACK_ATTACHMENTS:

            payload = {
                "username": "alerta",
                "channel": "#alerts",
                "text": summary,
                "icon_emoji": ":rocket:"
            }

        else:
            payload = {
                "username": "alerta",
                "channel": "#alerts",
                "icon_emoji": ":rocket:",
                "attachments": [{
                    "fallback": summary,
                    "color": color,
                    "pretext": text,
                    "fields": [
                        {"title": "Status", "value": alert.status.capitalize(), "short": True},
                        {"title": "Environment", "value": alert.environment, "short": True},
                        {"title": "Resource", "value": alert.resource, "short": True},
                        {"title": "Event", "value": alert.event, "short": True}
                    ]
                }]
            }

        LOG.debug('Slack payload: %s', payload)

        try:
            r = requests.post(url, data=json.dumps(payload), timeout=2)
        except Exception as e:
            raise RuntimeError("Slack connection error: %s", e)

        LOG.debug('Slack response: %s', r.status_code)


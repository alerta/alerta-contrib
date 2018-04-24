import logging

from alerta.plugins import PluginBase
from alertaclient.api import Client

LOG = logging.getLogger('alerta.plugins.forward')

FORWARD_URL = app.config.get('FORWARD_URL')
FORWARD_API = app.config.get('FORWARD_API')

class ForwardAlert(PluginBase):

    def pre_receive(self, alert):
        return

    def post_receive(self, alert):
        if not FORWARD_URL or not FORWARD_API:
            return
        client = Client(key=FORWARD_API, endpoint=FORWARD_URL)
        client.send_event(
            event=alert.get('event'),
            resource=alert.get('resource'),
            alert
        )
        return

    def status_change(self, alert, status, text):
        return

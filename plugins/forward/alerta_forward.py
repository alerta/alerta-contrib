import logging

from alerta.plugins import PluginBase
from alertaclient.api import Client

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.forward')

FORWARD_URL = app.config.get('FORWARD_URL')
FORWARD_API_KEY = app.config.get('FORWARD_API_KEY')
FORWARD_MAX_LENGTH = app.config.get('FORWARD_MAX_LENGTH') or 3

class ForwardAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if not FORWARD_URL or not FORWARD_API_KEY:
            return
        client = Client(endpoint=FORWARD_URL, key=FORWARD_API_KEY)
        fw_alert = alert.serialize
        event = fw_alert.pop('event')
        resource = fw_alert.pop('resource')
        fw_count = alert.attributes.get('fw_count') or 0
        fw_count = fw_count+1
        if fw_count >= FORWARD_MAX_LENGTH:
            LOG.debug('alert discarded by cycle overflow')
            return

        fw_alert.get('attributes')['fw_count'] = fw_count
        client.send_alert(
            event=event,
            resource=resource,
            **fw_alert
        )
        return

    def status_change(self, alert, status, text):
        return

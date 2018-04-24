import logging

from alerta.plugins import PluginBase
from alertaclient.api import Client

LOG = logging.getLogger('alerta.plugins.forward')

FORWARD_URL = app.config.get('FORWARD_URL')
FORWARD_API_KEY = app.config.get('FORWARD_API_KEY')
FORWARD_MAX_LENGTH = app.config.get('FORWARD_MAX_LENGTH') or 3

class ForwardAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if not FORWARD_URL or not FORWARD_API:
            return
        client = Client(endpoint=FORWARD_URL, key=FORWARD_API_KEY)
        forwarded_alert = alert.del['event']
        forwarded_alert = forwarded_alert.del['resource']
        fw_count = forwarded_alert.attributes.get('fw_count') or 0
        fw_count = fw_count+1
        if fw_count >= FORWARD_MAX_LENGTH:
            LOG.debug('alert discarded by cycle overflow')
            return
        client.send_event(
            event=alert.get('event'),
            resource=alert.get('resource'),
            forwarded_alert
        )
        return

    def status_change(self, alert, status, text):
        return

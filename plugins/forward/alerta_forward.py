import os
import logging

from alerta.plugins import PluginBase
from alertaclient.api import Client

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.forward')

FORWARD_URL = os.environ.get(
    'FORWARD_URL') or app.config.get('FORWARD_URL')
FORWARD_API_KEY = os.environ.get(
    'FORWARD_API_KEY') or app.config.get('FORWARD_API_KEY')
FORWARD_MAX_LENGTH = os.environ.get(
    'FORWARD_MAX_LENGTH') or app.config.get('FORWARD_MAX_LENGTH') or 3

class ForwardAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if not FORWARD_URL or not FORWARD_API_KEY:
            return
        client = Client(endpoint=FORWARD_URL, key=FORWARD_API_KEY)
        fw_count = alert.attributes.get('fw_count') or 0
        fw_count = fw_count+1
        if fw_count >= FORWARD_MAX_LENGTH:
            LOG.debug('alert discarded by cycle overflow')
            return

        alert.attributes['fw_count'] = fw_count
        client.send_alert(
            **alert.serialize
        )
        return

    def status_change(self, alert, status, text):
        return

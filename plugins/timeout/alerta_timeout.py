import os
import logging

from alerta.app import app
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.timeout')

TIMEOUT = os.environ.get('ALERT_TIMEOUT') or app.config.get('ALERT_TIMEOUT', '2600')

class Timeout(PluginBase):

    def pre_receive(self, alert):

        LOG.debug("Setting timeout for alert to %s ",TIMEOUT)
        alert.timeout = TIMEOUT

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
import os
import logging

from alerta.app import app
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.customtimeout')

CUSTOM_TIMEOUT = os.environ.get('CUSTOM_TIMEOUT') or app.config.get('CUSTOM_TIMEOUT', '2600')

class CustomTimeout(PluginBase):

    def pre_receive(self, alert):

        LOG.debug("Setting timeout for alert to %s ",CUSTOM_TIMEOUT)
        alert.timeout = CUSTOM_TIMEOUT

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
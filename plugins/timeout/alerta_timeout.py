import logging
import os

from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.timeout')

TIMEOUT = os.environ.get('ALERT_TIMEOUT') or app.config.get(
    'ALERT_TIMEOUT', '2600')


class Timeout(PluginBase):

    def pre_receive(self, alert):

        LOG.debug('Setting timeout for alert to %s ', TIMEOUT)
        alert.timeout = TIMEOUT

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

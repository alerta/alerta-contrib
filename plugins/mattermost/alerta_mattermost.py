import logging
import os

from alerta.plugins import PluginBase
from matterhook import Webhook

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0


LOG = logging.getLogger('alerta.plugins.mattermost')

MATTERMOST_URL = os.environ.get(
    'MATTERMOST_URL') or app.config['MATTERMOST_URL']
MATTERMOST_TOKEN = os.environ.get(
    'MATTERMOST_TOKEN') or app.config['MATTERMOST_TOKEN']
MATTERMOST_USERNAME = os.environ.get(
    'MATTERMOST_USERNAME') or app.config.get(
    'MATTERMOST_USERNAME', 'alerta')


class ServiceIntegration(PluginBase):

    def pre_receive(self, alert):
        LOG.debug('Mattermost: %s', alert)
        return alert

    def get_icon(self, status):
        LOG.debug('Mattermost: %s', status)
        return {
            'security': ':closed_lock_with_key:',
            'critical': ':bangbang:',
            'major': ':exclamation:',
            'minor': ':grey_exclamation:',
            'warning': ':warning:',
            'informational': ':info:',
            'debug': ':clock3:',
            'trace': ':signal_strength:',
            'ok': ':ok:'
        }.get(status, ':ok:')

    def _prepare_payload(self, alert):
        LOG.debug('Mattermost: %s', alert)
        return '{} **{}** **{}**\n`{}` ```{}```'.format(
            self.get_icon(alert.severity),
            alert.severity,
            alert.environment,
            alert.event,
            alert.text,
        )

    def post_receive(self, alert):
        if alert.repeat:
            return

        mwh = Webhook(MATTERMOST_URL, MATTERMOST_TOKEN)
        mwh.username = MATTERMOST_USERNAME
        message = self._prepare_payload(alert)
        LOG.debug('Mattermost: %s', message)
        mwh.send(message)

    def status_change(self, alert, status, text):
        pass

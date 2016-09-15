import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info("Normalising alert...")

        alert.text = '%s: %s' % (alert.severity.upper(), alert.text)

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

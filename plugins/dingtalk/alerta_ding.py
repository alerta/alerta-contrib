from dingtalkchatbot.chatbot import DingtalkChatbot
import time
import json
import sys
import os
import logging

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase



LOG = logging.getLogger('alerta.plugins.ding')


DING_WEBHOOK_URL = os.environ.get('DING_WEBHOOK_URL') or app.config.get('DING_WEBHOOK_URL')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')



class ServiceIntegration(PluginBase):

    def __init__(self, name=None):

        super().__init__(name)

    def pre_receive(self, alert):
        return alert


    def _prepare_payload(self, alert):
        return "{}** **{}**\n`{}` ```{}```".format(
            alert.severity,
            alert.environment,
            alert.event,
            alert.value,
        )
        LOG.debug('DingTalk: %s', alert)



    def post_receive(self, alert):
        if alert.repeat:
            return

        ding = DingtalkChatbot(DING_WEBHOOK_URL)
        message = self._prepare_payload(alert)
        LOG.debug('DingTalk: %s', message)
        ding.send_text(msg='Received Alert {}'.format(message))
#xiaoding.send_text(msg='next alert {}'.format(service_name_str))


       
    def status_change(self, alert, status, text):
        return



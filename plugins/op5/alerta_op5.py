
import os
import datetime
from op5 import OP5
import logging

from alerta.app import app
from alerta.app import db
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.op5')

DEFAULT_OP5_API_URL = 'https://demo.op5.com/api'

OP5_API_URL = os.environ.get('OP5_API_URL') or app.config.get('OP5_API_URL', None)
OP5_API_USERNAME = os.environ.get('OP5_API_USERNAME') or app.config.get('OP5_API_USERNAME', '')
OP5_API_PASSWORD = os.environ.get('OP5_API_PASSWORD') or app.config.get('OP5_API_PASSWORD', '')


class OP5Acknowledge(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):

        if alert.event_type not in ('op5ServiceAlert', 'op5HostAlert'):
            return

        if alert.status == status:
            return

        if status == 'ack':
            json_data = {"sticky":"1","notify":"0","persistent":"1","comment": text}
            if alert.event_type == 'op5ServiceAlert':
                command_type = 'ACKNOWLEDGE_SVC_PROBLEM'
                json_data["host_name"] = alert.resource
                json_data["service_description"] = alert.event
            if alert.event_type == 'op5HostAlert':
                command_type = 'ACKNOWLEDGE_HOST_PROBLEM'
                json_data["host_name"] = alert.resource
            
            op5 = OP5(OP5_API_URL, OP5_API_USERNAME, OP5_API_PASSWORD, dryrun=False, debug=False, logtofile=False, interactive=False)
            op5.command(command_type, json_data)

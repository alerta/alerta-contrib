
import os
import logging

from alerta.app import app
from alerta.plugins import PluginBase

from pyzabbix import ZabbixAPI, ZabbixAPIException

LOG = logging.getLogger('alerta.plugins.zabbix')

ZABBIX_API_URL = os.environ.get('ZABBIX_API_URL') or app.config['ZABBIX_API_URL']
ZABBIX_USER = os.environ.get('ZABBIX_USER') or app.config['ZABBIX_USER']
ZABBIX_PASSWORD = os.environ.get('ZABBIX_PASSWORD') or app.config['ZABBIX_PASSWORD']

NO_ACTION = 0
ACTION_CLOSE = 1


class ZabbixEventAck(PluginBase):

    def __init__(self, name=None):

        self.zapi = ZabbixAPI(ZABBIX_API_URL)
        self.zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
        LOG.debug("Connected to Zabbix API Version %s" % self.zapi.api_version())

        super(ZabbixEventAck, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):

        if alert.event_type != 'zabbixAlert':
            return

        if alert.status == status:
            return

        if status == 'ack':
            action = NO_ACTION
        elif status == 'closed':
            action = ACTION_CLOSE
        else:
            return

        event_id = alert.attributes.get('eventId', None)
        if event_id:
            LOG.debug('Zabbix: acknowledge event=%s, resource=%s (eventId=%s) ', alert.event, alert.resource, event_id)
            try:
                r = self.zapi.event.acknowledge(eventids=event_id, message=text, action=action)
            except ZabbixAPIException as e:
                raise RuntimeError("Zabbix: ERROR - %s", e)
            LOG.debug('Zabbix: %s', r)

            text = text + ' (Zabbix problem %s)' % 'closed' if action == ACTION_CLOSE else 'acknowledged'
        else:
            LOG.error('Zabbix: eventId is missing from alert attributes')

        return alert, status, text

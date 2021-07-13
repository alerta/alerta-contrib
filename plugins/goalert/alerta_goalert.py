import logging
import os
import re
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.goalert')
LOG.info('Initializing')

GOALERT_URL = os.environ.get('GOALERT_URL') or app.config['GOALERT_URL'] 
GOALERT_TOKEN = os.environ.get('GOALERT_TOKEN') or app.config['GOALERT_TOKEN']
GOALERT_VERIFY = os.environ.get('GOALERT_VERIFY') or app.config['GOALERT_VERIFY']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config['DASHBOARD_URL']

class TriggerEvent(PluginBase):

    def goalerts_endpoint(self):
        return '%s%s' % (GOALERT_URL, '/api/v2/generic/incoming')

    def goalert_close_alert(self, alert, why):
        closeUrl = self.goalerts_endpoint()

        json = {
            "token": GOALERT_TOKEN,
            "dedup": alert.id,
            "action": "close"
        }
        LOG.debug('goalert close %s: %s %s' % (why, alert.id, closeUrl))

        try:
            r = requests.post(closeUrl, json, timeout=2, verify=GOALERT_VERIFY)
        except Exception as e:
            raise RuntimeError("goalert connection error: %s" % e)
        return r

    # def goalert_ack_alert(self, alert, why):

    #     ackUrl = goalert_EVENTS_ACK_URL % alert.id
    #     LOG.debug('goalert ack %s: %s %s' % (why, alert.id, ackUrl))

    #     try:
    #         r = requests.post(ackUrl, json={}, headers=headers, timeout=2)
    #     except Exception as e:
    #         raise RuntimeError("goalert connection error: %s" % e)
    #     return r

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        LOG.debug('Alert receive %s: %s' % (alert.id, alert.get_body(history=False)))
        if alert.repeat:
            LOG.debug('Alert repeating; ignored')
            return

        if (alert.severity in ['cleared', 'normal', 'ok']) or (alert.status == 'closed'):
            r = self.goalert_close_alert(alert, 'CREATE-CLOSE')
        else:
            body = alert.get_body(history=False)
            json = {
                "token": GOALERT_TOKEN,
                "dedup": alert.id,
                "summary": alert.resource,
                "details": "[%s] %s: %s" % (alert.environment, alert.resource, alert.value)
            }
            LOG.debug('goalert CREATE payload: %s' % json)
            endpoint = self.goalerts_endpoint()

            try:
                r = requests.post(endpoint, json, timeout=2, verify=GOALERT_VERIFY)
            except Exception as e:
                raise RuntimeError("goalert connection error: %s" % e)

            LOG.debug('goalert response: %s - %s' % (r.status_code, r.text))

    def status_change(self, alert, status, text):
        LOG.debug('Alert change %s to %s: %s' % (alert.id, status, alert.get_body(history=False)))

        if status not in ['ack', 'assign', 'closed']:
            LOG.debug('Not sending status change to goalert: %s to %s' % (alert.id, status))
            return

        if status == 'closed':
            r = self.goalert_close_alert(alert, 'STATUS-CLOSE')
        # elif status == 'ack':
        #     r = self.goalert_ack_alert(alert, 'STATUS-ACK')

        LOG.debug('goalert response: %s - %s' % (r.status_code, r.text))

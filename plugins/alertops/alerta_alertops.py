import logging
import os
import re
import requests

from alerta.exceptions import RejectException
from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins')

ALERTOPS_WEBHOOK_URL = os.environ.get('AO_URL') or app.config['AO_URL']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config['DASHBOARD_URL']


class TriggerEvent(PluginBase):


    def pre_receive(self, alert, **kwargs):
        
        return alert

    def post_receive(self, alert, **kwargs):
        if alert.repeat:
                return
        message = "%s: %s alert for %s - %s" %( alert.environment, alert.severity.capitalize(), ','.join(alert.service), alert.resource)
        
        if alert.severity in ['cleared', 'normal', 'ok']:
                event_type = "close"
        else:
                event_type = "open"                

        payload = {
            "source_id": alert.id,
            "source_status": event_type,
            "description": message,
            "resource": alert.resource,
            "source": "alerta",
            "source_url": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
            "details": alert.get_body(history=False)}
        LOG.debug('AlertOps Payload: %s', payload)

        try:
            r = requests.post(ALERTOPS_WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("AlertOps connection error: %s" % e)
        LOG.debug('AlertOps response: %s - %s' % (r.status_code, r.text))
        return

    def status_change(self, alert, status, text, **kwargs):
        if status not in ['ack', 'assign']:
                return 
        message = "%s: %s alert for %s - %s" %( alert.environment, alert.severity.capitalize(), ','.join(alert.service), alert.resource)
        payload = {
            "source_id": alert.id,
            "source_status": event_type,
            "description": message,
            "resource": alert.resource,
            "source": "alerta",
            "source_url": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
            "details": alert.get_body(history=False)}

        try:
            r = requests.post(ALERTOPS_WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("AlertOps connection error: %s" % e)
        LOG.debug('AlertOps response: %s - %s' % (r.status_code, r.text))
        


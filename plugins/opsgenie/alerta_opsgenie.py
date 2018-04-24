
import logging
import os
import re
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.opsgenie')
LOG.info('Initializing')

OPSGENIE_EVENTS_CREATE_URL = 'https://api.opsgenie.com/v1/json/alert'
OPSGENIE_EVENTS_CLOSE_URL = 'https://api.opsgenie.com/v1/json/alert/close'
OPSGENIE_SERVICE_KEY = os.environ.get('OPSGENIE_SERVICE_KEY') or app.config['OPSGENIE_SERVICE_KEY']
SERVICE_KEY_MATCHERS = os.environ.get('SERVICE_KEY_MATCHERS') or app.config['SERVICE_KEY_MATCHERS']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')
LOG.info('Initialized: %s key, %s matchers' % (OPSGENIE_SERVICE_KEY, SERVICE_KEY_MATCHERS))

class TriggerEvent(PluginBase):

    def opsgenie_service_key(self, resource):
        if not SERVICE_KEY_MATCHERS:
            LOG.debug('No matchers defined! Default service key: %s' % (OPSGENIE_SERVICE_KEY))
            return OPSGENIE_SERVICE_KEY

        for mapping in SERVICE_KEY_MATCHERS:
            if re.match(mapping['regex'], resource):
                LOG.debug('Matched regex: %s, service key: %s' % (mapping['regex'], mapping['api_key']))
                return mapping['api_key']

        LOG.debug('No regex match! Default service key: %s' % (OPSGENIE_SERVICE_KEY))
        return OPSGENIE_SERVICE_KEY

    def opsgenie_close_alert(self, alert, why):

        payload = {
            "apiKey": self.opsgenie_service_key(alert.resource),
            "alias": alert.id
        }

        LOG.debug('OpsGenie %s payload: %s' % (why, payload))

        try:
            r = requests.post(OPSGENIE_EVENTS_CLOSE_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("OpsGenie connection error: %s" % e)
        return r

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        LOG.debug('Alert receive %s: %s' % (alert.id, alert.get_body(history=False)))
        if alert.repeat:
            LOG.debug('Alert repeating; ignored')
            return

        # If alerta has cleared or status is closed, send the close to opsgenie
        if (alert.severity in ['cleared', 'normal', 'ok']) or (alert.status == 'closed'):
            r = self.opsgenie_close_alert(alert, 'CREATE-CLOSE')

        else:
            # Send all alert data as details to opsgenie
            details = alert.get_body(history=False)
            details['web_url'] = '%s/#/alert/%s' % (DASHBOARD_URL, alert.id)

            payload = {
                "apiKey": self.opsgenie_service_key(alert.resource),
                "alias": alert.id,
                "message": "[ %s ]: %s: %s" % (alert.environment, alert.severity, alert.text),
                "entity": alert.environment,
                "teams" : [],
                "tags": "%s,%s,%s,%s" % (alert.environment, alert.resource, alert.service[0], alert.event),
                "details": details
            }

            LOG.debug('OpsGenie CREATE payload: %s', payload)

            try:
                r = requests.post(OPSGENIE_EVENTS_CREATE_URL, json=payload, timeout=2)
            except Exception as e:
                raise RuntimeError("OpsGenie connection error: %s" % e)

        LOG.debug('OpsGenie response: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):
        LOG.debug('Alert change %s: %s' % (alert.id, alert.get_body(history=False)))

        if status not in ['ack', 'assign']:
            return

        r = self.opsgenie_close_alert(alert, 'STATUS-CLOSE')

        LOG.debug('OpsGenie response: %s - %s', r.status_code, r.text)

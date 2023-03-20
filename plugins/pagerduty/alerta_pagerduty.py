import logging
import os
import re

import requests
from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.pagerduty')

PAGERDUTY_EVENTS_URL = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
PAGERDUTY_SERVICE_KEY = os.environ.get(
    'PAGERDUTY_SERVICE_KEY') or app.config['PAGERDUTY_SERVICE_KEY']
SERVICE_KEY_MATCHERS = os.environ.get(
    'SERVICE_KEY_MATCHERS') or app.config['SERVICE_KEY_MATCHERS']
DASHBOARD_URL = os.environ.get(
    'DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TriggerEvent(PluginBase):

    def pagerduty_service_key(self, resource):
        if not SERVICE_KEY_MATCHERS:
            LOG.debug('No matchers defined! Default service key: %s' %
                      (PAGERDUTY_SERVICE_KEY))
            return PAGERDUTY_SERVICE_KEY

        for mapping in SERVICE_KEY_MATCHERS:
            if re.match(mapping['regex'], resource):
                LOG.debug('Matched regex: %s, service key: %s' %
                          (mapping['regex'], mapping['api_key']))
                return mapping['api_key']

        LOG.debug('No regex match! Default service key: %s' %
                  (PAGERDUTY_SERVICE_KEY))
        return PAGERDUTY_SERVICE_KEY

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        message = '{}: {} alert for {} - {} is {}'.format(
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )

        if alert.severity in ['cleared', 'normal', 'ok']:
            event_type = 'resolve'
        else:
            event_type = 'trigger'

        payload = {
            'service_key': self.pagerduty_service_key(alert.resource),
            'incident_key': alert.id,
            'event_type': event_type,
            'description': message,
            'client': 'alerta',
            'client_url': '{}/#/alert/{}'.format(DASHBOARD_URL, alert.id),
            'details': alert.get_body(history=False)
        }

        LOG.debug('PagerDuty payload: %s', payload)

        try:
            r = requests.post(PAGERDUTY_EVENTS_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError('PagerDuty connection error: %s' % e)

        LOG.debug('PagerDuty response: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):

        if status not in ['ack', 'assign']:
            return

        payload = {
            'service_key': self.pagerduty_service_key(alert.resource),
            'incident_key': alert.id,
            'event_type': 'acknowledge',
            'description': text,
            'details': alert.get_body(history=False)
        }

        LOG.debug('PagerDuty payload: %s', payload)

        try:
            r = requests.post(PAGERDUTY_EVENTS_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError('PagerDuty connection error: %s' % e)

        LOG.debug('PagerDuty response: %s - %s', r.status_code, r.text)

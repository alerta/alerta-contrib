
import os
import json
import requests

from alertaclient.app import app
from alertaclient.plugins import PluginBase

LOG = app.logger

PAGERDUTY_EVENTS_URL = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
PAGERDUTY_SERVICE_KEY = os.environ.get('PAGERDUTY_SERVICE_KEY') or app.config['PAGERDUTY_SERVICE_KEY']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TriggerEvent(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.repeat:
            return

        message = "%s: %s alert for %s - %s is %s" % (
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )

        if alert.severity in ['cleared', 'normal', 'ok']:
            event_type = "resolve"
        else:
            event_type = "trigger"

        payload = {
            "service_key": PAGERDUTY_SERVICE_KEY,
            "incident_key": alert.id,
            "event_type": event_type,
            "description": message,
            "client": "alerta",
            "client_url": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
            "details": alert.get_body(history=False)
        }

        LOG.debug('PagerDuty payload: %s', payload)

        try:
            r = requests.post(PAGERDUTY_EVENTS_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("PagerDuty connection error: %s" % e)

        LOG.debug('PagerDuty response: %s - %s', r.status_code, r.text)

    def status_change(self, alert, status, text):

        if status not in ['ack', 'assign']:
            return

        payload = {
            "service_key": PAGERDUTY_SERVICE_KEY,
            "incident_key": alert.id,
            "event_type": "acknowledge",
            "description": text,
            "details": alert.get_body(history=False)
        }

        LOG.debug('PagerDuty payload: %s', payload)

        try:
            r = requests.post(PAGERDUTY_EVENTS_URL, json=payload, timeout=2)
        except Exception as e:
            raise RuntimeError("PagerDuty connection error: %s" % e)

        LOG.debug('PagerDuty response: %s - %s', r.status_code, r.text)

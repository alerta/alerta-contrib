
import logging
import os
import re
import requests
import pdpyras

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.pagerduty')

# PAGERDUTY_EVENTS_URL = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
PAGERDUTY_SERVICE_KEY = os.environ.get('PAGERDUTY_SERVICE_KEY') or app.config['PAGERDUTY_SERVICE_KEY']
SERVICE_KEY_MATCHERS = os.environ.get('SERVICE_KEY_MATCHERS') or app.config['SERVICE_KEY_MATCHERS']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TriggerEvent(PluginBase):

    def pagerduty_service_key(self, resource):
        if not SERVICE_KEY_MATCHERS:
            LOG.warning('No matchers defined! Default service key: %s' % (PAGERDUTY_SERVICE_KEY))
            return PAGERDUTY_SERVICE_KEY

        for mapping in SERVICE_KEY_MATCHERS:
            if re.match(mapping['regex'], resource):
                LOG.warning('Matched regex: %s, service key: %s' % (mapping['regex'], mapping['api_key']))
                return mapping['api_key']

        LOG.warning('No regex match! Default service key: %s' % (PAGERDUTY_SERVICE_KEY))
        return PAGERDUTY_SERVICE_KEY

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):

        LOG.warning('Sending PagerDuty notice')

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

        # payload = {
        #     "service_key": self.pagerduty_service_key(alert.resource),
        #     "incident_key": alert.id,
        #     "event_type": event_type,
        #     "description": message,
        #     "client": "alerta",
        #     "client_url": '%s/#/alert/%s' % (DASHBOARD_URL, alert.id),
        #     "details": alert.get_body(history=False)
        # }

        session = pdpyras.EventsAPISession(self.pagerduty_service_key(alert.resource))
        # payload = {
        #     "type": "incident",
        #     "summary": message,
        #     "severity": "critical",
        #     "source": "alerta",
        #     "custom_details": alert.get_body(history=False)
        # }

        try:
            pd_incident = session.trigger(message, alert.resource, dedup_key=alert.id)
        except Exception as e:
            raise RuntimeError("PagerDuty connection error: %s" % e)

        LOG.warning('PagerDuty notice sent')

    def status_change(self, alert, status, text, **kwargs):

        if status not in ['ack', 'assign']:
            return

        session = pdpyras.EventsAPISession(self.pagerduty_service_key(alert.resource))

        # payload = {
        #     "incident_key": alert.id,
        #     "summary": text,
        #     "custom_details": alert.get_body(history=False)
        # }

        LOG.warn('PagerDuty status change ignored.')

        try:
            # r = requests.post(PAGERDUTY_EVENTS_URL, json=payload, timeout=2)
            pass
            # pd_incident = session.resolve(alert.id)
        except Exception as e:
            raise RuntimeError("PagerDuty connection error: %s" % e)

        # LOG.debug('PagerDuty response: %s - %s', r.status_code, r.text)

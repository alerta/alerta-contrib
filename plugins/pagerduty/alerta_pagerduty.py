
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

PAGERDUTY_SERVICE_KEY = os.environ.get('PAGERDUTY_SERVICE_KEY') or app.config['PAGERDUTY_SERVICE_KEY']
SERVICE_KEY_MATCHERS = os.environ.get('SERVICE_KEY_MATCHERS') or app.config['SERVICE_KEY_MATCHERS']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')


class TriggerEvent(PluginBase):

    def pagerduty_service_key(self, resource):
        if not SERVICE_KEY_MATCHERS:
            LOG.debug('No matchers defined! Default service key: %s' % (PAGERDUTY_SERVICE_KEY))
            return PAGERDUTY_SERVICE_KEY

        for mapping in SERVICE_KEY_MATCHERS:
            if re.match(mapping['regex'], resource):
                LOG.debug('Matched regex: %s, service key: %s' % (mapping['regex'], mapping['api_key']))
                return mapping['api_key']

        LOG.debug('No regex match! Default service key: %s' % (PAGERDUTY_SERVICE_KEY))
        return PAGERDUTY_SERVICE_KEY

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):

        LOG.debug('Sending PagerDuty notice')

        if alert.repeat:
            return

        message = "%s: %s alert for %s - %s is %s" % (
            alert.environment, alert.severity.capitalize(),
            ','.join(alert.service), alert.resource, alert.event
        )

        session = pdpyras.EventsAPISession(self.pagerduty_service_key(alert.resource))

        try:
            if alert.severity in ['cleared', 'normal', 'ok']:
                pd_incident = session.resolve(alert.id)
            else:
                pd_incident = session.trigger(
                    message,
                    alert.resource,
                    dedup_key=alert.id,
                    severity=alert.severity,
                    custom_details=alert.get_body(history=False),
                    links=['%s/#/alert/%s' % (DASHBOARD_URL, alert.id)]
                )

        except Exception as e:
            raise RuntimeError("PagerDuty connection error: %s" % e)

        LOG.info('PagerDuty notice sent')

    def status_change(self, alert, status, text, **kwargs):
        LOG.debug('PagerDuty status change ignored.')


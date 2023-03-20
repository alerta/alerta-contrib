import logging
import os

import requests
from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.geoip')

GEOIP_URL = os.environ.get('GEOIP_URL') or app.config.get(
    'GEOIP_URL', 'http://api.ipstack.com')
GEOIP_ACCESS_KEY = os.environ.get(
    'GEOIP_ACCESS_KEY') or app.config.get('GEOIP_ACCESS_KEY', None)


class GeoLocation(PluginBase):

    def pre_receive(self, alert):

        ip_addr = alert.attributes['ip'].split(', ')[0]
        LOG.debug('GeoIP lookup for IP: %s', ip_addr)

        if 'ip' in alert.attributes:
            url = '{}/{}?access_key={}'.format(GEOIP_URL,
                                               ip_addr, GEOIP_ACCESS_KEY)
        else:
            LOG.warning('IP address must be included as an alert attribute.')
            raise RuntimeWarning(
                'IP address must be included as an alert attribute.')

        r = requests.get(
            url, headers={'Content-type': 'application/json'}, timeout=2)
        try:
            geoip_lookup = r.json()
            alert.attributes = {
                'geoip': geoip_lookup,
                'country': geoip_lookup['location'].get('country_flag_emoji')
            }
        except Exception as e:
            LOG.error('GeoIP lookup failed: %s' % str(e))
            raise RuntimeError('GeoIP lookup failed: %s' % str(e))

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

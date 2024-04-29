import logging
import os

import requests
from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.ip2locationpy')

IP2LOCATIONIO_URL = 'https://api.ip2location.io'
IP2LOCATIONIO_ACCESS_KEY = os.environ.get(
    'IP2LOCATIONIO_ACCESS_KEY') or app.config.get('IP2LOCATIONIO_ACCESS_KEY', None)


class IP2Locationio(PluginBase):

    def pre_receive(self, alert):

        if 'ip' in alert.attributes:
            ip_addr = alert.attributes['ip'].split(', ')[0]
            LOG.debug('IP2Location.io lookup for IP: %s', ip_addr)
            url = '{}/?key={}&ip={}'.format(IP2LOCATIONIO_URL, IP2LOCATIONIO_ACCESS_KEY,
                                               ip_addr)
        else:
            LOG.warning('IP address must be included as an alert attribute.')
            raise RuntimeWarning(
                'IP address must be included as an alert attribute.')

        r = requests.get(
            url, headers={'Content-type': 'application/json'}, timeout=2)
        LOG.debug('Result: %s', r.text)
        try:
            ip2locationio_result = r.json()
            if 'country' in ip2locationio_result and 'language' in ip2locationio_result['country']:
                ip2locationio_result['country']['official_language'] = ip2locationio_result['country'].pop('language')
            alert.attributes = {
                'ip2locationio_result': ip2locationio_result
            }
        except Exception as e:
            LOG.error('IP2Location.io lookup failed: %s' % str(e))
            raise RuntimeError('IP2Location.io lookup failed: %s' % str(e))

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

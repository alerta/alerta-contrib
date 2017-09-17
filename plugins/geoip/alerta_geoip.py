
import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.geoip')

GEOIP_URL = os.environ.get('GEOIP_URL') or app.config.get('GEOIP_URL', 'http://freegeoip.net/json')


class GeoLocation(PluginBase):

    def pre_receive(self, alert):

        ip_addr = alert.attributes['ip'].split(', ')[0]
        LOG.debug("GeoIP lookup for IP: %s", ip_addr)

        if 'ip' in alert.attributes:
            url = '%s/%s' % (GEOIP_URL, ip_addr)
        else:
            LOG.warning("IP address must be included as an alert attribute.")
            raise RuntimeWarning("IP address must be included as an alert attribute.")

        r = requests.get(url, headers={'Content-type': 'application/json'}, timeout=2)
        try:
            alert.attributes['geoip'] = r.json()
        except Exception as e:
            LOG.error("GeoIP lookup failed: %s" % str(e))
            raise RuntimeError("GeoIP lookup failed: %s" % str(e))

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

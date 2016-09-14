
import os
import requests

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

GEOIP_URL = os.environ.get('GEOIP_URL') or app.config.get('GEOIP_URL', 'http://freegeoip.net/json')


class GeoLocation(PluginBase):

    def pre_receive(self, alert):

        if 'ip' in alert.attributes:
            url = '%s/%s' % (GEOIP_URL, alert.attributes['ip'])
        else:
            raise RuntimeWarning("IP address must be included as an alert attribute.")

        r = requests.get(url, headers={'Content-type': 'application/json'}, timeout=2)
        try:
            alert.attributes.update(r.json())
        except Exception as e:
            raise RuntimeError("GeoIP lookup failed: %s" % str(e))

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

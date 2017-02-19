
import os
import logging
import json

from alerta.app import app
from alerta.plugins import PluginBase

import cachetclient.cachet as cachet

LOG = logging.getLogger('alerta.plugins.cachet')

CACHET_API_URL = os.environ.get('CACHET_API_URL') or app.config['CACHET_API_URL']
CACHET_API_TOKEN = os.environ.get('CACHET_API_TOKEN') or app.config['CACHET_API_TOKEN']
CACHET_SSL_VERIFY = True if (os.environ.get('CACHET_SSL_VERIFY') == 'True' or app.config.get('CACHET_SSL_VERIFY', False)) else False


STATUS_MAP = {
    'open': 1,  # Investigating
    'ack': 2,  # Identified
    'assigned': 3,  # Watching
    'closed': 4  # Fixed
}

class CachetIncident(PluginBase):

    def __init__(self, name=None):

        self.incidents = cachet.Incidents(endpoint=CACHET_API_URL, api_token=CACHET_API_TOKEN, verify=CACHET_SSL_VERIFY)

        super(CachetIncident, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        name = alert.event
        status = STATUS_MAP[alert.status]
        message = alert.text

        r = json.loads(self.incidents.get(name=name, message=message, status=status))
        if r['meta']['pagination']['count']:
            return

        try:
            r = json.loads(self.incidents.post(name=name, message=message, status=status, visible=True))
        except Exception as e:
            raise RuntimeError("Cachet: ERROR - %s", e)

        LOG.debug('Cachet: %s', r)

    def status_change(self, alert, status, text):
        return

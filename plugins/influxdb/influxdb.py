
import os
import json
import requests

from alerta.app import app
from alerta.plugins import PluginBase

LOG = app.logger

INFLUXDB_URL = os.environ.get('INFLUXDB_URL') or app.config['INFLUXDB_URL']
INFLUXDB_USER = os.environ.get('INFLUXDB_USER') or app.config['INFLUXDB_USER']
INFLUXDB_PASSWORD = os.environ.get('INFLUXDB_PASSWORD') or app.config['INFLUXDB_PASSWORD']


class InfluxDBWrite(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        url = INFLUXDB_URL + '/db/alerta/series'

        data = [{
            "name": alert.event,
            "columns": ["value", "environment", "resource"],
            "points": [
                [alert.value, alert.environment, alert.resource]
            ]
        }]

        LOG.debug('InfluxDB data: %s', data)

        try:
            response = requests.post(url=url, data=json.dumps(data), auth=(INFLUXDB_USER, INFLUXDB_PASSWORD))
        except Exception as e:
            raise RuntimeError("InfluxDB connection error: %s", e)

        LOG.debug('InfluxDB response: %s', response)

    def status_change(self, alert, status, text):
        return

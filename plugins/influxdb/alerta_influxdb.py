
import os
import json
import logging

from alerta.app import app
from alerta.plugins import PluginBase

from influxdb import InfluxDBClient

LOG = logging.getLogger('alerta.plugins.influxdb')

DEFAULT_INFLUXDB_DSN = 'influxdb://user:pass@localhost:8086/alerta' # 'influxdb://username:password@localhost:8086/databasename'

INFLUXDB_DSN = os.environ.get('INFLUXDB_DSN') or app.config.get('INFLUXDB_DSN', DEFAULT_INFLUXDB_DSN)
INFLUXDB_DATABASE = os.environ.get('INFLUXDB_DATABASE') or app.config.get('INFLUXDB_DATABASE', None)


class InfluxDBWrite(PluginBase):

    def __init__(self, name=None):

        self.client = InfluxDBClient.from_DSN(INFLUXDB_DSN, timeout=2)

        dbname = INFLUXDB_DATABASE or self.client._database
        try:
            if dbname:
                self.client.switch_database(dbname)
        except Exception as e:
            print e

        super(InfluxDBWrite, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        points = [
            {
                "measurement": alert.event,
                "tags": {
                    "resource": alert.resource,
                    "environment": alert.environment
                },
                "time": alert.last_receive_time,
                "fields": {
                    "value": alert.value
                }
            }
        ]
        LOG.debug('InfluxDB: %s', points)

        try:
            self.client.write_points(points, time_precision='ms', tags=alert.attributes)
        except Exception as e:
            raise RuntimeError("InfluxDB: ERROR - %s" % e)

    def status_change(self, alert, status, text):
        return

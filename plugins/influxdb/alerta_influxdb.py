
import logging
import os

from datetime import datetime

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

from influxdb import InfluxDBClient

LOG = logging.getLogger('alerta.plugins.influxdb')

# 'influxdb://username:password@localhost:8086/databasename'
DEFAULT_INFLUXDB_DSN = 'influxdb://user:pass@localhost:8086/alerta'

INFLUXDB_DSN = os.environ.get('INFLUXDB_DSN') or app.config.get('INFLUXDB_DSN', DEFAULT_INFLUXDB_DSN)
INFLUXDB_DATABASE = os.environ.get('INFLUXDB_DATABASE') or app.config.get('INFLUXDB_DATABASE', None)

# Specify the name of a measurement to which all alerts will be logged
INFLUXDB_MEASUREMENT = os.environ.get('INFLUXDB_MEASUREMENT') or app.config.get('INFLUXDB_MEASUREMENT', 'event')


class InfluxDBWrite(PluginBase):

    def __init__(self, name=None):

        self.client = InfluxDBClient.from_dsn(INFLUXDB_DSN, timeout=2)

        dbname = INFLUXDB_DATABASE or self.client._database
        try:
            if dbname:
                self.client.switch_database(dbname)
                self.client.create_database(dbname)
        except Exception as e:
            LOG.error('InfluxDB: ERROR - %s' % e)

        super(InfluxDBWrite, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def _influxdb_prepare_point(self, alert, status=None, text=None):
        tags = {}

        for tag in alert.tags:
            try:
                k, v = tag.split('=', 1)
                tags[k] = v
            except ValueError:
                pass

        tags.update(
            event=alert.event,
            resource=alert.resource,
            environment=alert.environment,
            severity=alert.severity,
            status=status if status else alert.status,
            service=','.join(alert.service)
        )
        if alert.customer:
            tags.update(customer=alert.customer)

        # event data
        point = {
            'measurement': INFLUXDB_MEASUREMENT,
            'time': datetime.utcnow() if status else alert.create_time,
            'tags': tags,
            'fields': {}
        }

        # make sure we store the value in its original format
        if isinstance(alert.value, float) or isinstance(alert.value, int):
            point['fields']['value'] = alert.value
        else:
            point['fields']['value'] = str(alert.value)

        if text:
            point['fields']['text'] = text

        return point

    def post_receive(self, alert):
        point = self._influxdb_prepare_point(alert)
        LOG.debug('InfluxDB: point=%s', point)

        try:
            self.client.write_points([point], time_precision='ms')
        except Exception as e:
            raise RuntimeError("InfluxDB: ERROR - %s" % e)

    def status_change(self, alert, status, text):
        if status not in ['ack', 'assign']:
            return

        point = self._influxdb_prepare_point(alert, status, text)
        LOG.debug('InfluxDB: point=%s', point)

        try:
            self.client.write_points([point], time_precision='ms')
        except Exception as e:
            raise RuntimeError("InfluxDB: ERROR - %s" % e)

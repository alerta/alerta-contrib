
import logging
import os

from kombu import BrokerConnection, Exchange, Producer
from kombu.utils.debug import setup_logging

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.amqp')

DEFAULT_AMQP_URL = 'mongodb://localhost:27017/kombu'
DEFAULT_AMQP_TOPIC = 'notify'
DEFAULT_AMQP_SEND_ALERT_HISTORY = True

AMQP_URL = os.environ.get('REDIS_URL') or os.environ.get('AMQP_URL') or app.config.get('AMQP_URL', DEFAULT_AMQP_URL)
AMQP_TOPIC = os.environ.get('AMQP_TOPIC') or app.config.get('AMQP_TOPIC', DEFAULT_AMQP_TOPIC)


class FanoutPublisher(PluginBase):

    def __init__(self, name=None):
        if app.config['DEBUG']:
            setup_logging(loglevel='DEBUG', loggers=[''])

        self.connection = BrokerConnection(AMQP_URL)
        try:
            self.connection.connect()
        except Exception as e:
            LOG.error('Failed to connect to AMQP transport %s: %s', AMQP_URL, e)
            raise RuntimeError

        self.channel = self.connection.channel()
        self.exchange_name = AMQP_TOPIC

        self.exchange = Exchange(name=self.exchange_name, type='fanout', channel=self.channel)
        self.producer = Producer(exchange=self.exchange, channel=self.channel)

        super(FanoutPublisher, self).__init__(name)

        LOG.info('Configured fanout publisher on topic "%s"', AMQP_TOPIC)

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):
        LOG.info('Sending message %s to AMQP topic "%s"', alert.get_id(), AMQP_TOPIC)
        body = alert.get_body(history=self.get_config('AMQP_SEND_ALERT_HISTORY', default=DEFAULT_AMQP_SEND_ALERT_HISTORY, type=bool, **kwargs))
        LOG.debug('Message: %s', body)
        self.producer.publish(body, declare=[self.exchange], retry=True)

    def status_change(self, alert, status, text, **kwargs):
        return

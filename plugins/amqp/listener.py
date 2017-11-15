#!/usr/bin/env python

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin

AMQP_URL = 'mongodb://localhost:27017/kombu'
AMQP_TOPIC = 'notify'


class FanoutConsumer(ConsumerMixin):
    def __init__(self, conn):
        self.connection = conn
        self.channel = self.connection.channel()

    def get_consumers(self, Consumer, channel):
        exchange = Exchange(
            name=AMQP_TOPIC,
            type='fanout',
            channel=self.channel,
            durable=True
        )
        queues = [
            Queue(
                name='',
                exchange=exchange,
                routing_key='',
                channel=self.channel,
                exclusive=True
            )
        ]
        return [
            Consumer(queues=queues, accept=['json'], callbacks=[self.on_message])
        ]

    def on_message(self, body, message):
        try:
            print(body)
        except Exception as e:
            print(str(e))
        message.ack()

if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='DEBUG', loggers=[''])
    with Connection(AMQP_URL) as conn:
        consumer = FanoutConsumer(conn)
        consumer.run()

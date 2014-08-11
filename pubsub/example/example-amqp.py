#!/usr/bin/env python

from kombu import BrokerConnection, Exchange, Queue
from kombu.mixins import ConsumerMixin

BROKER_URL = 'amqp://guest:guest@localhost:5672//'


class Worker(ConsumerMixin):

    def __init__(self, connection):

        self.connection = connection
        self.exchange = Exchange('alerts', type='direct', durable=True)
        self.queue = Queue('alerts', exchange=self.exchange, routing_key='alerts')

    def get_consumers(self, Consumer, channel):

        return [
            Consumer(queues=[self.queue], callbacks=[self.on_message], accept=['json']),
        ]

    def on_message(self, body, message):

        print("RECEIVED MESSAGE: %r" % (body, ))
        message.ack()


def main():

    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='DEBUG')

    with BrokerConnection(BROKER_URL) as connection:
        try:
            Worker(connection).run()
        except KeyboardInterrupt:
            print('Exiting...')

if __name__ == '__main__':
    main()

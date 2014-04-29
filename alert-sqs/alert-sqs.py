#!/usr/bin/env python

import settings

from kombu import Connection, Exchange, Queue, Producer
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging

from alert import Alert, ApiClient

#setup_logging(loglevel='DEBUG', loggers=[''])

sqs_queue = getattr(settings, 'sqs_queue', 'alerta')
exchange = Exchange('sqs', type='direct')
queue = Queue(sqs_queue, exchange, routing_key=sqs_queue)


class Worker(ConsumerMixin):

    def __init__(self, connection):

        self.connection = connection
        self.api = ApiClient()

    def get_consumers(self, Consumer, channel):

        return [
            Consumer(queues=queue, callbacks=[self.on_message])
        ]

    def on_message(self, body, message):

        print self.api.send_alert(Alert(**body))
        message.ack()


def main():

    broker_url = getattr(settings, 'broker_url', 'sqs://')
    transport_options = getattr(settings, 'transport_options', {'region': 'eu-west-1'})

    with Connection(broker_url, transport_options=transport_options) as conn:

        channel = conn.channel()
        queue(channel).declare()

        # testing only
        test = Alert('foo', 'bar', attributes={'this': 'that'}, tags=['abc', 'def'])
        producer = Producer(channel, exchange, routing_key=sqs_queue)
        producer.publish(test.get_body())

        Worker(conn).run()


if __name__ == '__main__':

    main()

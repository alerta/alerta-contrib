#!/usr/bin/env python

import settings

from alert import Alert
from kombu import BrokerConnection

__version__ = '3.0.0'

# from kombu.utils.debug import setup_logging
# setup_logging(loglevel='DEBUG', loggers=[''])


def main():

    broker_url = getattr(settings, 'broker_url', 'sqs://')
    transport_options = getattr(settings, 'transport_options', {'region': 'eu-west-1'})
    sqs_queue = getattr(settings, 'sqs_queue', 'alerta')

    connection = BrokerConnection(broker_url, transport_options=transport_options)
    queue = connection.SimpleQueue(sqs_queue)

    alert = Alert('foo', 'bar', severity='major', service='test', environment='production')
    queue.put(alert.get_body())
    queue.close()

if __name__ == '__main__':
    main()
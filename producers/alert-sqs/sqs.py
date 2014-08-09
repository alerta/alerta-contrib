#!/usr/bin/env python

import os
import settings

from alert import Alert, Heartbeat, ApiClient
from kombu import BrokerConnection
from Queue import Empty

__version__ = '3.0.0'

from kombu.utils.debug import setup_logging
# setup_logging(loglevel='DEBUG', loggers=[''])


def main():

    broker_url = getattr(settings, 'broker_url', 'sqs://')
    transport_options = getattr(settings, 'transport_options', {'region': 'eu-west-1'})
    sqs_queue = getattr(settings, 'sqs_queue', 'alerta')

    connection = BrokerConnection(broker_url, transport_options=transport_options)
    queue = connection.SimpleQueue(sqs_queue)

    api = ApiClient()

    while True:
        try:
            message = queue.get(block=True, timeout=20)
            print message.payload
            api.send_alert(Alert(**message.payload))
            message.ack()
        except Empty:
            pass
        except (KeyboardInterrupt, SystemExit):
            break

        api.send_heartbeat(Heartbeat(origin='alert-sqs/%s' % os.uname()[1], tags=[__version__]))

    queue.close()


if __name__ == '__main__':
    main()

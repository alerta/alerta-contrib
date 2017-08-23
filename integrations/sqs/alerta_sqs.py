#!/usr/bin/env python

import os
import sys
import time
import logging

from flask.config import Config

import boto.sqs
from boto.sqs.message import RawMessage
from boto import exception

LOG = logging.getLogger('alerta.sqs')

config = Config('/')
config.from_pyfile('/etc/alertad.conf', silent=True)
config.from_envvar('ALERTA_SVR_CONF_FILE', silent=True)

DEFAULT_AWS_REGION = 'eu-west-1'
DEFAULT_AWS_SQS_QUEUE = 'alerts'

AWS_REGION = os.environ.get('AWS_REGION') or config.get('AWS_REGION', DEFAULT_AWS_REGION)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or config.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or config.get('AWS_SECRET_ACCESS_KEY')
AWS_SQS_QUEUE = os.environ.get('AWS_SQS_QUEUE') or config.get('AWS_SQS_QUEUE', DEFAULT_AWS_SQS_QUEUE)


class Worker(object):

    def __init__(self):

        try:
            connection = boto.sqs.connect_to_region(
                AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        except boto.exception.SQSError as e:
            LOG.error('SQS: ERROR - %s' % e)
            sys.exit(1)

        try:
            self.sqs = connection.create_queue(AWS_SQS_QUEUE)
            self.sqs.set_message_class(RawMessage)
        except boto.exception.SQSError as e:
            LOG.error('SQS: ERROR - %s' % e)
            sys.exit(1)

    def run(self):

        while True:
            LOG.debug('Waiting for alert on SQS queue "%s"...' % AWS_SQS_QUEUE)
            try:
                message = self.sqs.read(wait_time_seconds=20)
            except boto.exception.SQSError as e:
                LOG.error('SQS: ERROR - %s' % e)
                time.sleep(20)
                continue

            if message:
                self.process_message(message)

    def process_message(self, message):
        LOG.info('SQS: Received message - %s' % message.get_body())
        self.sqs.delete_message(message)


def main():
    try:
        Worker().run()
    except (SystemExit, KeyboardInterrupt):
        sys.exit(0)

if __name__ == '__main__':
    main()

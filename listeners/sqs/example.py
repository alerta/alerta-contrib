#!/usr/bin/env python

import sys
import time
import json
import logging

import boto
from boto.sqs.message import RawMessage
from boto import exception

__version__ = '3.3.0'

LOG = logging.getLogger(__name__)

AWS_SQS_QUEUE = 'example'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_REGION = 'eu-west-1'


class Worker(object):

    def __init__(self):

        try:
            connection = boto.sqs.connect_to_region(
                AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        except boto.exception.SQSError as e:
            LOG.error('SQS API call failed: %s', e)
            sys.exit(1)

        try:
            self.sqs = connection.create_queue(AWS_SQS_QUEUE)
            self.sqs.set_message_class(RawMessage)
        except boto.exception.SQSError as e:
            LOG.error('SQS queue error: %s', e)
            sys.exit(1)

    def run(self):

        while True:
            LOG.debug('Waiting for alert on %s...', AWS_SQS_QUEUE)
            try:
                notification = self.sqs.read(wait_time_seconds=20)
            except boto.exception.SQSError as e:
                LOG.warning('Could not read from queue: %s', e)
                time.sleep(20)
                continue

            if notification:
                body = json.loads(notification.get_body())
                LOG.info("Message Body: %s", json.dumps(body, indent=4))
                LOG.info("Message Payload: %s", body['Message'])
                self.sqs.delete_message(notification)


def main():

    logging.basicConfig(format="%(asctime)s - %(name)s: %(levelname)s - %(message)s", level=logging.INFO)

    try:
        Worker().run()
    except (SystemExit, KeyboardInterrupt):
        return

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import sys
import time
import logging

import boto.sqs
from boto.sqs.message import RawMessage

__version__ = '3.2.0'

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
        except boto.exception.SQSError, e:
            sys.exit(1)

        try:
            self.sqs = connection.create_queue(AWS_SQS_QUEUE)
            self.sqs.set_message_class(RawMessage)
        except boto.exception.SQSError, e:
            sys.exit(1)

    def run(self):

        while True:
            print 'Waiting for alert on %s...' % AWS_SQS_QUEUE
            try:
                message = self.sqs.read(wait_time_seconds=20)
            except boto.exception.SQSError, e:
                time.sleep(20)
                continue

            if message:
                print("RECEIVED MESSAGE: %r" % message.get_body())
                self.sqs.delete_message(message)


def main():

    try:
        Worker().run()
    except (SystemExit, KeyboardInterrupt):
        return

if __name__ == '__main__':
    main()

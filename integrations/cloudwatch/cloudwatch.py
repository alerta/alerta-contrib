
import os
import sys
import json
import time
import datetime

import boto.sqs
from boto.sqs.message import RawMessage
from boto import exception

from alerta.api import ApiClient
from alerta.alert import Alert
from alerta.heartbeat import Heartbeat

__version__ = '3.2.0'

AWS_SQS_QUEUE = os.environ.get('AWS_SQS_QUEUE')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

ALERTA_ENDPOINT = os.environ.get('ALERTA_ENDPOINT')
ALERTA_API_KEY = os.environ.get('ALERTA_API_KEY')

AWS_ACCOUNT_ID = {
    '101234567890': 'aws-account-name'
}


class CloudWatch(object):

    def __init__(self):

        self.api = ApiClient(key=ALERTA_API_KEY)

        try:
            connection = boto.sqs.connect_to_region(
                AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        except boto.exception.SQSError as e:
            print >>sys.stderr, 'SQS API call failed: %s' % e
            sys.exit(1)

        try:
            self.sqs = connection.create_queue(AWS_SQS_QUEUE)
            self.sqs.set_message_class(RawMessage)
        except boto.exception.SQSError as e:
            print >>sys.stderr, 'SQS queue error: %s' % e
            sys.exit(1)

    def run(self):

        while True:
            print 'Waiting for CloudWatch alarms on %s...' % AWS_SQS_QUEUE
            try:
                message = self.sqs.read(wait_time_seconds=20)
            except boto.exception.SQSError as e:
                print >>sys.stderr, 'Could not read from queue: %s' % e
                time.sleep(20)
                continue

            if message:
                body = message.get_body()
                cloudwatchAlert = self.parse_notification(body)
                try:
                    self.api.send(cloudwatchAlert)
                except Exception as e:
                    print >>sys.stderr, 'Failed to send alert: %s' % e
                self.sqs.delete_message(message)

            print 'Send heartbeat...'
            heartbeat = Heartbeat(origin='alerta-cloudwatch', tags=[__version__])
            try:
                self.api.send(heartbeat)
            except Exception as e:
                print >>sys.stderr, 'Failed to send heartbeat: %s' % e

    def parse_notification(self, message):

        notification = json.loads(message)
        if 'Message' in notification:
            alarm = json.loads(notification['Message'])
        else:
            return

        if 'Trigger' not in alarm:
            return

        # Defaults
        resource = '%s:%s' % (alarm['Trigger']['Dimensions'][0]['name'], alarm['Trigger']['Dimensions'][0]['value'])
        event = alarm['AlarmName']
        severity = self.cw_state_to_severity(alarm['NewStateValue'])
        group = 'CloudWatch'
        value = alarm['AlarmDescription']
        text = notification['Subject']
        environment = 'Production'
        service = [AWS_ACCOUNT_ID.get(alarm['AWSAccountId'], 'AWSAccountId:' + alarm['AWSAccountId'])]
        tags = [alarm['Trigger']['MetricName'], alarm['Trigger']['Namespace']]
        correlate = list()
        origin = notification['TopicArn']
        timeout = None
        create_time = datetime.datetime.strptime(notification['Timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        raw_data = notification['Message']

        cloudwatchAlert = Alert(
            resource=resource,
            event=event,
            correlate=correlate,
            group=group,
            value=value,
            severity=severity,
            environment=environment,
            service=service,
            text=text,
            event_type='cloudwatchAlarm',
            tags=tags,
            attributes={
                'awsMessageId': notification['MessageId'],
                'awsRegion': alarm['Region'],
                'thresholdInfo': alarm['NewStateReason']
            },
            origin=origin,
            timeout=timeout,
            create_time=create_time,
            raw_data=raw_data,
        )

        return cloudwatchAlert

    @staticmethod
    def cw_state_to_severity(state):

        if state == 'ALARM':
            return 'major'
        elif state == 'INSUFFICIENT_DATA':
            return 'warning'
        elif state == 'OK':
            return 'normal'
        else:
            return 'unknown'


def main():

    try:
        CloudWatch().run()
    except (SystemExit, KeyboardInterrupt):
        print 'Exiting...'


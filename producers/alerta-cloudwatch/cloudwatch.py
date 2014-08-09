
import sys
import json
import time
import datetime
import logging

import boto.sqs
from boto.sqs.message import RawMessage
from boto import exception

from alerta.api import ApiClient
from alerta.alert import Alert
from alerta.heartbeat import Heartbeat

LOG = logging.getLogger(__name__)

logging.basicConfig(filename='example.log', level=logging.DEBUG)

__version__ = '3.2.0'


class CloudWatch(object):

    def __init__(self):

        self.aws_region = 'eu-west-1'
        self.aws_sqs_queue = ''
        self.aws_access_key = ''
        self.aws_secret_key = ''

        self.api = ApiClient()  # does this pick up endpoint and key from config files?

    def run(self):

        try:
            connection = boto.sqs.connect_to_region(
                self.aws_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
        except boto.exception.SQSError, e:
            LOG.error('SQS API call failed: %s', e)
            sys.exit(1)

        try:
            sqs = connection.create_queue(self.aws_sqs_queue)
            sqs.set_message_class(RawMessage)
        except boto.exception.SQSError, e:
            LOG.error('SQS queue error: %s', e)
            sys.exit(1)

        while True:
            try:
                LOG.info('Waiting for CloudWatch alarms...')
                try:
                    message = sqs.read(wait_time_seconds=20)
                except boto.exception.SQSError, e:
                    LOG.warning('Could not read from queue: %s', e)
                    time.sleep(20)
                    continue

                if message:
                    body = message.get_body()
                    cloudwatchAlert = self.parse_notification(body)
                    try:
                        self.api.send(cloudwatchAlert)
                    except Exception, e:
                        LOG.warning('Failed to send alert: %s', e)
                    sqs.delete_message(message)

                LOG.debug('Send heartbeat...')
                heartbeat = Heartbeat(tags=[__version__])
                try:
                    self.api.send(heartbeat)
                except Exception, e:
                    LOG.warning('Failed to send heartbeat: %s', e)

            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def parse_notification(self, message):

        LOG.debug('Parsing CloudWatch notification message...')

        notification = json.loads(message)
        if 'Message' in notification:
            alarm = notification['Message']
        else:
            return

        if 'Trigger' not in alarm:
            return

        # Defaults
        resource = alarm['Trigger']['Dimensions'][0]['value']
        event = alarm['AlarmName']
        severity = self.cw_state_to_severity(alarm['NewStateValue'])
        group = 'CloudWatch'
        value = alarm['NewStateValue']
        text = alarm['AlarmDescription']
        environment = ['INFRA']
        service = [alarm['AWSAccountId']]
        tags = [notification['MessageId'], alarm['Region']]
        correlate = list()
        origin = [notification['TopicArn']]
        timeout = None
        threshold_info = alarm['NewStateReason']
        more_info = notification['Subject']
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
                'thresholdInfo': threshold_info,
                'moreInfo': more_info
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


def shell():

    cw = CloudWatch()
    return cw.run()

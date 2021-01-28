
import boto3
import logging
import os

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.sns')

DEFAULT_AWS_REGION = 'eu-west-1'
DEFAULT_AWS_SNS_TOPIC = 'notify'

AWS_REGION = os.environ.get('AWS_REGION') or app.config.get('AWS_REGION', DEFAULT_AWS_REGION)
AWS_SNS_TOPIC = os.environ.get('AWS_SNS_TOPIC') or app.config.get('AWS_SNS_TOPIC', DEFAULT_AWS_SNS_TOPIC)


class SnsTopicPublisher(PluginBase):

    def __init__(self, name=None):
        try:
            self.client = boto3.client('sns')
            #     region_name=AWS_REGION,
            # )
        except Exception as e:
            LOG.error('Error connecting to SNS topic %s: %s', AWS_SNS_TOPIC, e)
            raise RuntimeError

        if not self.client:
            LOG.error('Failed to connect to SNS topic %s - check AWS credentials and region', AWS_SNS_TOPIC)
            raise RuntimeError

        try:
            response = self.client.create_topic(
                Name=AWS_SNS_TOPIC,
                FifoTopic=True if AWS_SNS_TOPIC.endswith('fifo') else False
            )
        except self.client.exception.BotoServerError as e:
            LOG.error('Error creating SNS topic %s: %s', AWS_SNS_TOPIC, e)
            raise RuntimeError

        try:
            self.topic_arn = response['CreateTopicResponse']['CreateTopicResult']['TopicArn']
        except KeyError:
            LOG.error('Failed to get SNS TopicArn for %s', AWS_SNS_TOPIC)
            raise RuntimeError

        super(SnsTopicPublisher, self).__init__(name)

        LOG.info('Configured SNS publisher on topic "%s"', self.topic_arn)

    def pre_receive(self, alert, **kwargs):
        return alert

    def post_receive(self, alert, **kwargs):

        LOG.info('Sending message %s to SNS topic "%s"', alert.get_id(), self.topic_arn)
        LOG.debug('Message: %s', alert.get_body())

        response = self.client.publish(
            TopicArn=self.topic_arn,
            Subject='Alert {} received'.format(alert.last_receive_id),
            MessageStructure='json',
            Message=alert.get_body(),
            MessageAttributes={
                'resource': {
                    'DataType': 'string',
                    'StringValue': alert.resource
                },
                'event': {
                    'DataType': 'string',
                    'StringValue': alert.event
                },
                'environment': {
                    'DataType': 'string',
                    'StringValue': alert.environment
                },
                'severity': {
                    'DataType': 'string',
                    'StringValue': alert.severity
                },
                'status': {
                    'DataType': 'string',
                    'StringValue': alert.status
                },
            },
            MessageDeduplicationId=alert.last_receive_id,
            MessageGroupId=alert.id
        )
        LOG.debug('Response: %s', response)

    def status_change(self, alert, status, text, **kwargs):
        return

import os

import boto.sns
import boto.exception

from alertaclient.app import app
from alertaclient.plugins import PluginBase

LOG = app.logger

DEFAULT_AWS_REGION = 'eu-west-1'
DEFAULT_AWS_SNS_TOPIC = 'notify'

AWS_REGION = os.environ.get('AWS_REGION') or app.config.get('AWS_REGION', DEFAULT_AWS_REGION)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or app.config.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or app.config.get('AWS_SECRET_ACCESS_KEY')
AWS_SNS_TOPIC = os.environ.get('AWS_SNS_TOPIC') or app.config.get('AWS_SNS_TOPIC', DEFAULT_AWS_SNS_TOPIC)


class SnsTopicPublisher(PluginBase):

    def __init__(self, name=None):
        try:
            self.connection = boto.sns.connect_to_region(
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            LOG.error('Error connecting to SNS topic %s: %s', AWS_SNS_TOPIC, e)
            raise RuntimeError

        if not self.connection:
            LOG.error('Failed to connect to SNS topic %s - check AWS credentials and region', AWS_SNS_TOPIC)
            raise RuntimeError

        try:
            response = self.connection.create_topic(AWS_SNS_TOPIC)
        except boto.exception.BotoServerError as e:
            LOG.error('Error creating SNS topic %s: %s', AWS_SNS_TOPIC, e)
            raise RuntimeError

        try:
            self.topic_arn = response['CreateTopicResponse']['CreateTopicResult']['TopicArn']
        except KeyError:
            LOG.error('Failed to get SNS TopicArn for %s', AWS_SNS_TOPIC)
            raise RuntimeError

        super(SnsTopicPublisher, self).__init__(name)

        LOG.info('Configured SNS publisher on topic "%s"', self.topic_arn)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        LOG.info('Sending message %s to SNS topic "%s"', alert.get_id(), self.topic_arn)
        LOG.debug('Message: %s', alert.get_body())

        response = self.connection.publish(topic=self.topic_arn, message=alert.get_body())
        LOG.debug('Response: %s', response)

    def status_change(self, alert, status, text):
        return
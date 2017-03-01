
import os
import logging

from alerta.app import app
from alerta.plugins import PluginBase

from google.cloud import pubsub

LOG = logging.getLogger('alerta.plugins.pubsub')
DEFAULT_TOPIC_NAME = 'alerta'
TOPIC_NAME = os.environ.get('TOPIC_NAME') or app.config.get('TOPIC_NAME', DEFAULT_TOPIC_NAME)

DEFAULT_SUBSCRIPTION_NAME = 'alerta-notification'
SUBSCRIPTION_NAME = os.environ.get('SUBSCRIPTION_NAME') or app.config.get('SUBSCRIPTION_NAME', DEFAULT_SUBSCRIPTION_NAME)


class SendToPubsub(PluginBase):

    def __init__(self, name=None):

        self.client = pubsub.Client()

        # create pubsub topic and subscription if does not exists
        try:
            self.topic = self.client.topic(TOPIC_NAME)

            if not self.topic.exists():
                LOG.info('creating pubsub topic')
                self.topic.create()
            subscription = self.topic.subscription(SUBSCRIPTION_NAME)
            if not subscription.exists():
                LOG.info('creating pubsub topic subscription')
                subscription.create()
        except Exception as excp:
            LOG.exception(excp)
            raise RuntimeError("pubsub exception")

        super(SendToPubsub, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        try:
            message_id = self.topic.publish(alert.__str__())
            LOG.info('message %s published', message_id)
        except Exception as excp:
            LOG.exception(excp)
            raise RuntimeError("pubsub exception")

    def status_change(self, alert, status, text):
        return

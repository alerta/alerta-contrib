
import logging
import os

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

from google.cloud import pubsub
from google.oauth2 import service_account


LOG = logging.getLogger('alerta.plugins.pubsub')

DEFAULT_TOPIC_NAME = 'alerta'
TOPIC_NAME = os.environ.get('TOPIC_NAME') or app.config.get('TOPIC_NAME', DEFAULT_TOPIC_NAME)

DEFAULT_SUBSCRIPTION_NAME = 'alerta-notification'
SUBSCRIPTION_NAME = os.environ.get('SUBSCRIPTION_NAME') or app.config.get('SUBSCRIPTION_NAME', DEFAULT_SUBSCRIPTION_NAME)

DEFAULT_SERVICE_ACCOUNT_FILE = None
SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE') or app.config.get('SERVICE_ACCOUNT_FILE', DEFAULT_SERVICE_ACCOUNT_FILE)

PUBSUB_SCOPES = ["https://www.googleapis.com/auth/pubsub"]

class SendToPubsub(PluginBase):

    def __init__(self, name=None):
        LOG.info('creating pubsub client')
        self.client = self.get_client()

        # create pubsub topic and subscription if does not exists
        try:
            LOG.info('checking pubsub topic')
            self.topic = self.client.topic(TOPIC_NAME)
            if not self.topic.exists():
                LOG.info('creating pubsub topic')
                self.topic.create()

            LOG.info('checking pubsub subscription')
            subscription = self.topic.subscription(SUBSCRIPTION_NAME)
            if not subscription.exists():
                LOG.info('creating pubsub topic subscription')
                subscription.create()

        except Exception as excp:
            LOG.exception(excp)
            raise RuntimeError("pubsub exception")

        super(SendToPubsub, self).__init__(name)

    def get_client(self):
        if SERVICE_ACCOUNT_FILE:
            LOG.info('using service account file %s', SERVICE_ACCOUNT_FILE)
            credential = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
            scoped_credential = credential.with_scopes(PUBSUB_SCOPES)
            return pubsub.Client(credentials=scoped_credential)

        LOG.info('default')
        return pubsub.Client()

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

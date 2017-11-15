import os
import logging
import base64
import json

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.plugins import PluginBase

from google.cloud import pubsub
from google.oauth2 import service_account

LOG = logging.getLogger('alerta.plugins.pubsub')

PROJECT_ID = os.environ.get('PROJECT_ID') or app.config.get('PROJECT_ID')
TOPIC_NAME = os.environ.get('TOPIC_NAME') or app.config.get('TOPIC_NAME')

SERVICE_ACCOUNT_JSON = os.environ.get('SERVICE_ACCOUNT_JSON') or app.config.get('SERVICE_ACCOUNT_JSON', None)

PUBSUB_SCOPES = ["https://www.googleapis.com/auth/pubsub"]

class SendToPubsub(PluginBase):

    def __init__(self, name=None):
        LOG.info('creating pubsub client')
        self.publisher = self.get_client()
        self.topic = 'projects/{}/topics/{}'.format(PROJECT_ID, TOPIC_NAME)
        super(SendToPubsub, self).__init__(name)

    def get_client(self):
        if SERVICE_ACCOUNT_JSON:
            json_dict = json.loads(SERVICE_ACCOUNT_JSON)
            LOG.info('using service account JSON : %s', json_dict)
            credential =  service_account.Credentials.from_service_account_info(json_dict)
            scoped_credential = credential.with_scopes(PUBSUB_SCOPES)
            return pubsub.PublisherClient(credentials=scoped_credential)

        LOG.info('default')
        return pubsub.PublisherClient()

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        body = alert.get_body()
        try:
            encoded_message = base64.b64encode(json.dumps(body))
            future = self.publisher.publish(self.topic, str(encoded_message))
            future.result()
        except Exception as excp:
            LOG.exception(excp)
            raise RuntimeError("pubsub exception: %s - %s" % (excp, body))

    def status_change(self, alert, status, text):
        return

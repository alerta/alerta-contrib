import json
import logging
import os
from datetime import datetime

from alerta.plugins import PluginBase
from google.cloud import pubsub_v1
from google.oauth2 import service_account

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0


LOG = logging.getLogger('alerta.plugins.pubsub')

PROJECT_ID = os.environ.get('PROJECT_ID') or app.config.get('PROJECT_ID')
TOPIC_NAME = os.environ.get('TOPIC_NAME') or app.config.get('TOPIC_NAME')

SERVICE_ACCOUNT_JSON = os.environ.get(
    'SERVICE_ACCOUNT_JSON') or app.config.get('SERVICE_ACCOUNT_JSON', None)

PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']


class SendToPubsub(PluginBase):

    def __init__(self, name=None):
        LOG.info('creating pubsub client')
        self.publisher = self.get_client()
        self.topic = 'projects/{}/topics/{}'.format(PROJECT_ID, TOPIC_NAME)
        super().__init__(name)

    def get_client(self):
        if SERVICE_ACCOUNT_JSON:
            json_dict = json.loads(SERVICE_ACCOUNT_JSON)
            LOG.info('using service account JSON : %s', json_dict)
            credential = service_account.Credentials.from_service_account_info(
                json_dict)
            scoped_credential = credential.with_scopes(PUBSUB_SCOPES)
            return pubsub_v1.PublisherClient(credentials=scoped_credential)

        LOG.info('default')
        return pubsub_v1.PublisherClient()

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        body = alert.get_body(history=False)
        if alert.severity not in ['cleared', 'normal', 'ok']:
            try:
                encoded_message = json.dumps(body)
                encoded_message = encoded_message.encode('utf-8')
                LOG.info('post receive')
                LOG.info(encoded_message)
                future = self.publisher.publish(self.topic, encoded_message)
                future.result()
            except Exception as excp:
                LOG.exception(excp)
                raise RuntimeError(
                    'pubsub exception: {} - {}'.format(excp, body))

    def status_change(self, alert, status, text):
        body = alert.get_body(history=False)
        if alert.severity not in ['normal', 'ok']:
            try:
                body['status'] = status
                body['updateTime'] = datetime.utcnow().isoformat()
                encoded_message = json.dumps(body)
                encoded_message = encoded_message.encode('utf-8')
                LOG.info('status change: %s', status)
                LOG.info(encoded_message)
                future = self.publisher.publish(self.topic, encoded_message)
                future.result()
            except Exception as excp:
                LOG.exception(excp)
                raise RuntimeError(
                    'pubsub exception: {} - {}'.format(excp, body))

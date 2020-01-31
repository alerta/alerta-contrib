
import json
import unittest

from alerta.app import create_app, custom_webhooks
from uuid import uuid4

import alerta_msteamswebhook

class MsteamsWebhookTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()
        custom_webhooks.webhooks['msteams'] = alerta_msteamswebhook.MsteamsWebhook()

        self.headers = {
            'X-API-Key': 'some_secret_string',
            'Authentication': 'Bearer fakestring-here',
            'Content-Type': 'application/json'
        }

        self.alert_id = 'f0c55228-c61d-462a-9aeb-f6048d37fdf6'

    def test_msteamswebhook(self):

        payload_cmd = """
            {
              "action": "%s",
              "alert_id": "%s"
            }
        """

        # Missing alert_id
        payload_invalidcmd = """
            {
              "action": "%s"
            }
        """

        payload_blackout = r"""
            {
              "action": "blackout",
              "environment": "Production",
              "resource": "webhooktest1",
              "event": "DiskUtilHigh"
            }
        """

        # ack
        # TODO: needs to mock Alert.find_by_id / alert.set_status
        #response = self.client.post('/webhooks/msteams', data=payload_cmd % ('ack', self.alert_id), content_type='application/json', headers=self.headers)
        #self.assertEqual(response.status_code, 200)
        #data = json.loads(response.data.decode('utf-8'))
        #self.assertEqual(data['status'], 'ok')
        #self.assertEqual(data['message'], 'status changed')
        #self.assertTrue(bool(response.headers.get('CARD-ACTION-STATUS', False)))

        # ack with missing alert_id
        response = self.client.post('/webhooks/msteams', data=payload_invalidcmd % 'ack', content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Missing/invalid alert_id')

        # ack with bogus alert_id
        response = self.client.post('/webhooks/msteams', data=payload_cmd % ('ack', '7a0e3ee1-fbaa-45th-isis-bogus'), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Missing/invalid alert_id')

        # close alert
        # TODO: needs to mock Alert.find_by_id / alert.set_status
        #response = self.client.post('/webhooks/msteams', data=payload_cmd % ('close', self.alert_id), content_type='application/json', headers=self.headers)
        #self.assertEqual(response.status_code, 200)
        #data = json.loads(response.data.decode('utf-8'))
        #self.assertEqual(data['status'], 'ok')
        #self.assertEqual(data['message'], 'status changed')
        #self.assertTrue(bool(response.headers.get('CARD-ACTION-STATUS', False)))

        # create blackout
        # TODO: needs to mock: blackout.create()
        #response = self.client.post('/webhooks/msteams', data=payload_blackout, content_type='application/json', headers=self.headers)
        #self.assertEqual(response.status_code, 201)
        #data = json.loads(response.data.decode('utf-8'))
        #self.assertEqual(data['status'], 'ok')
        #self.assertEqual(data['message'], 'blackout created')
        #self.assertTrue(bool(response.headers.get('CARD-ACTION-STATUS', False)))


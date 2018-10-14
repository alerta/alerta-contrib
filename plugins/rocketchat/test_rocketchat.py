import os
import json
import unittest
from uuid import uuid4

from alerta.app import create_app, db, plugins
from alerta.models.alert import Alert


class TestRocketChat(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False,
            'PLUGINS': ['rocketchat']
        }

        os.environ['ROCKETCHAT_WEBHOOK_URL'] = 'https://alerta.rocket.chat/hooks/Ahqyy84yFB4DuWorQ/ZyndPtdbY5PCnaQGsXTJPCXbNC9bDiTL9L2Q7ktLnuHFYNKd'

        self.app = create_app(test_config)
        self.client = self.app.test_client()

        self.alert = {'resource': 'node1', 'environment': 'Production', 'service': ['Test'], 'event': str(uuid4())}

    def tearDown(self):

        db.destroy()

    def test_register(self):

        self.assertEqual([k for k, v in plugins.plugins.items()], ['reject', 'blackout', 'rocketchat'])

    def test_pre_receive(self):

        plugins.plugins['rocketchat'].pre_receive(self.alert)

    def test_post_receive(self):

        response = self.client.post('/alert', json=self.alert, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))

        plugins.plugins['rocketchat'].post_receive(Alert.parse(data['alert']))

    def test_status_change(self):
        pass

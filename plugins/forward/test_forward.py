
import json
import unittest

from alerta.app import create_app, plugins
from alerta_slack import ServiceIntegration


class ForwardPluginTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False,
            'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

    def test_slack_plugin(self):

        plugins.plugins['slack'] = ServiceIntegration()

        self.alert = {
            'event': 'node_down',
            'resource': 'net5',
            'environment': 'Production',
            'service': ['Network'],
            'severity': 'critical',
            'correlate': ['node_down', 'node_marginal', 'node_up'],
            'tags': []
        }

        response = self.client.post('/alert', data=json.dumps(self.alert), headers={'Content-type': 'application/json'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')
        self.assertRegex(data['id'], '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


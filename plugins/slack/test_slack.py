import contextlib
import json
import os
import unittest

from alerta.app import create_app, plugins
from alerta_slack import ServiceIntegration


@contextlib.contextmanager
def mod_env(*remove, **update):
    """
    See https://stackoverflow.com/questions/2059482#34333710

    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


class SlackPluginTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_slack_plugin(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }

        with mod_env(
                SLACK_WEBHOOK_URL='https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        ):
            self.app = create_app(test_config)
            self.client = self.app.test_client()

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

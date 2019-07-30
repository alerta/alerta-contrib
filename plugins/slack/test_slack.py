import unittest
import alerta_slack

from collections import OrderedDict

from alerta.app import create_app, custom_webhooks

class ServiceIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.routeTags = OrderedDict({
            '#application1-major-team': ['application=application1', 'severity=major'],
            '#application1-minor-team': ['application=application1', 'severity=minor'],
            '#application2-major-team': ['application=application2', 'severity=major'],
            '#application2-team': ['application=application2'],
            '#default-alert-channel': 'default'
        })

        self.routeTagsWithoutDefault = OrderedDict({
            '#application1-major-team': ['application=application1', 'severity=major'],
            '#application1-minor-team': ['application=application1', 'severity=minor'],
            '#application2-major-team': ['application=application2', 'severity=major'],
            '#application2-team': ['application=application2']
        })

        self.routeTagsEmpty = OrderedDict()

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

    def test_default_route(self):
        alertTags = ['application=application3', 'severity=warning']
        self.assertEqual(alerta_slack.route_alert_by_tag(alertTags, self.routeTags), '#default-alert-channel')

        self.assertEqual(alerta_slack.route_alert_by_tag(alertTags, self.routeTagsWithoutDefault), '')
        self.assertEqual(alerta_slack.route_alert_by_tag(alertTags, self.routeTagsWithoutDefault, 'fallback'), 'fallback')

        self.assertEqual(alerta_slack.route_alert_by_tag(alertTags, self.routeTagsEmpty), '')
        self.assertEqual(alerta_slack.route_alert_by_tag(alertTags, self.routeTagsEmpty, 'fallback'), 'fallback')

    def test_route_order(self):
        alertTags1 = ['application=application2', 'severity=warning']
        self.assertEqual(alerta_slack.route_alert_by_tag(
            alertTags1, self.routeTags), '#application2-team')

        alertTags2 = ['application=application2']
        self.assertEqual(alerta_slack.route_alert_by_tag(
            alertTags2, self.routeTags), '#application2-team')

        alertTags3 = ['application=application2', 'severity=major']
        self.assertEqual(alerta_slack.route_alert_by_tag(
            alertTags3, self.routeTags), '#application2-major-team')

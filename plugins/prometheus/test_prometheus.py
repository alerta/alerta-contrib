"""
Unit tests for the Prometheus Alertmanager plugin.

API v2 request/response formats are based on the Alertmanager OpenAPI spec:
https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

os.environ['ALERTMANAGER_API_URL'] = 'http://alertmanager:9093'
os.environ['ALERTMANAGER_SILENCE_FROM_ACK'] = 'true'

from alerta.app import create_app  # noqa: E402
from alerta_prometheus import AlertmanagerSilence, parse_duration  # noqa: E402


class ParseDurationTestCase(unittest.TestCase):

    def test_integer_treated_as_days(self):
        assert parse_duration(1) == 86400
        assert parse_duration(7) == 604800

    def test_seconds(self):
        assert parse_duration('90s') == 90
        assert parse_duration('0s') == 0

    def test_minutes(self):
        assert parse_duration('30m') == 1800

    def test_hours(self):
        assert parse_duration('2h') == 7200

    def test_days(self):
        assert parse_duration('1d') == 86400

    def test_weeks(self):
        assert parse_duration('1w') == 604800

    def test_plain_integer_string_treated_as_days(self):
        assert parse_duration('3') == 259200

    def test_case_insensitive(self):
        assert parse_duration('2H') == 7200
        assert parse_duration('1D') == 86400

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            parse_duration('abc')
        with self.assertRaises(ValueError):
            parse_duration('10x')
        with self.assertRaises(ValueError):
            parse_duration('')


class AlertmanagerSilenceTestCase(unittest.TestCase):
    """
    Tests verify that the plugin uses Alertmanager API v2 endpoints and
    correctly handles v2 response formats per the OpenAPI spec:
    https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml
    """

    def setUp(self):
        config = {
            'TESTING': True,
            'AUTH_REQUIRED': False,
        }
        self.app = create_app(config)
        self.client = self.app.test_client()
        self.plugin = AlertmanagerSilence()

        # Create a prometheus alert
        self.prom_alert = {
            'event': 'DiskFull',
            'resource': 'web01',
            'environment': 'Production',
            'service': ['Web'],
            'severity': 'critical',
            'correlate': ['DiskFull', 'DiskOk'],
            'tags': [],
            'attributes': {},
            'raw_data': json.dumps({
                'labels': {'alertname': 'DiskFull', 'instance': 'web01'},
                'startsAt': '2024-01-01T00:00:00.000Z',
                'endsAt': '0001-01-01T00:00:00Z',
                'generatorURL': 'http://prometheus:9090/graph',
            }),
        }

    def _create_alert(self):
        """Create an alert via the API and return it."""
        response = self.client.post(
            '/alert', data=json.dumps(self.prom_alert),
            headers={'Content-type': 'application/json'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        alert_id = data['id']
        # Fetch the full alert object
        response = self.client.get('/alert/%s' % alert_id)
        data = json.loads(response.data.decode('utf-8'))
        return data['alert']

    @patch('alerta_prometheus.requests.post')
    def test_ack_creates_silence_via_v2_api(self, mock_post):
        """POST /api/v2/silences should be called on ack.

        Per the OpenAPI spec, the response is: {"silenceID": "<uuid>"}
        """
        # Mock the v2 silence creation response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"silenceID":"73373e3f-a928-450a-ba75-e9254297b483"}'
        mock_response.json.return_value = {
            'silenceID': '73373e3f-a928-450a-ba75-e9254297b483'
        }
        mock_post.return_value = mock_response

        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)
        alert.event_type = 'prometheusAlert'

        result = self.plugin.take_action(alert, 'ack', 'acked by user')

        # Verify v2 endpoint was called
        call_args = mock_post.call_args
        url = call_args[0][0]
        self.assertIn('/api/v2/silences', url)
        self.assertNotIn('/api/v1/', url)

        # Verify request body contains isRegex per v2 spec
        request_body = call_args[1]['json']
        for matcher in request_body['matchers']:
            self.assertIn('isRegex', matcher)
            self.assertFalse(matcher['isRegex'])

        # Verify required fields per v2 postableSilence schema
        self.assertIn('startsAt', request_body)
        self.assertIn('endsAt', request_body)
        self.assertIn('createdBy', request_body)
        self.assertIn('comment', request_body)

        # Verify silenceID was extracted from v2 response
        self.assertEqual(
            result.attributes['silenceId'],
            '73373e3f-a928-450a-ba75-e9254297b483')

    @patch('alerta_prometheus.requests.post')
    def test_close_expires_alert_via_v2_api(self, mock_post):
        """POST /api/v2/alerts should be called on close."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_post.return_value = mock_response

        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)
        alert.event_type = 'prometheusAlert'
        alert.raw_data = self.prom_alert['raw_data']

        self.plugin.take_action(alert, 'close', 'closing alert')

        call_args = mock_post.call_args
        url = call_args[0][0]
        self.assertIn('/api/v2/alerts', url)
        self.assertNotIn('/api/v1/', url)

    @patch('alerta_prometheus.requests.delete')
    def test_unack_deletes_silence_via_v2_api(self, mock_delete):
        """DELETE /api/v2/silence/{silenceID} should be called on unack."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_delete.return_value = mock_response

        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)
        alert.event_type = 'prometheusAlert'
        alert.attributes['silenceId'] = '73373e3f-a928-450a-ba75-e9254297b483'

        result = self.plugin.take_action(alert, 'unack', 'unacked')

        call_args = mock_delete.call_args
        url = call_args[0][0]
        self.assertIn('/api/v2/silence/73373e3f-a928-450a-ba75-e9254297b483',
                      url)
        self.assertNotIn('/api/v1/', url)

        # silenceId should be cleared
        self.assertIsNone(result.attributes['silenceId'])

    @patch('alerta_prometheus.requests.delete')
    def test_status_change_deletes_silence_via_v2_api(self, mock_delete):
        """DELETE /api/v2/silence/{silenceID} should be called on open/closed status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        mock_delete.return_value = mock_response

        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)
        alert.attributes['silenceId'] = 'abc-123'

        result = self.plugin.status_change(alert, 'open', '')

        call_args = mock_delete.call_args
        url = call_args[0][0]
        self.assertIn('/api/v2/silence/abc-123', url)
        self.assertNotIn('/api/v1/', url)
        self.assertIsNone(result.attributes['silenceId'])

    def test_non_prometheus_alert_ignored(self):
        """Non-prometheusAlert events should be returned unchanged."""
        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)
        alert.event_type = 'otherType'

        result = self.plugin.take_action(alert, 'ack', 'test')
        self.assertEqual(result, alert)

    def test_status_change_without_silence_is_noop(self):
        """Status change with no silenceId should not make any HTTP calls."""
        alert_data = self._create_alert()

        from alerta.models.alert import Alert
        alert = Alert.parse(alert_data)

        with patch('alerta_prometheus.requests.delete') as mock_delete:
            self.plugin.status_change(alert, 'open', '')
            mock_delete.assert_not_called()

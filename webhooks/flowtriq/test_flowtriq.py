import json
import unittest

import alerta_flowtriq
from alerta.app import create_app, custom_webhooks


class FlowtriqWebhookTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        custom_webhooks.webhooks['flowtriq'] = alerta_flowtriq.FlowtriqWebhook()

    def test_flowtriq_attack_start(self):
        """Test incoming DDoS attack start webhook."""

        attack_start = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_start",
            "timestamp": "2025-03-10T14:22:00Z",
            "incident": {
                "id": 147,
                "title": "UDP Flood on web-prod-1",
                "severity": "critical",
                "attack_family": "udp_flood",
                "peak_pps": 2450000,
                "peak_pps_fmt": "2.45M",
                "peak_bps": 1547000000,
                "peak_bps_fmt": "1.4 Gbps",
                "source_ip_count": 8429,
                "duration_seconds": 0,
                "duration_fmt": "",
                "ai_summary": "A large 1.4 Gbps UDP flood from 8,429 source IPs targeting web-prod-1",
                "status": "active",
                "started_at": "2025-03-10T14:22:00Z",
                "resolved_at": null,
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=147"
            },
            "node": {
                "name": "web-prod-1",
                "ip_address": "203.0.113.10"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=attack_start, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'web-prod-1')
        self.assertEqual(data['alert']['event'], 'DDoS_udp_flood')
        self.assertEqual(data['alert']['environment'], 'Production')
        self.assertEqual(data['alert']['severity'], 'critical')
        self.assertEqual(data['alert']['status'], 'open')
        self.assertEqual(data['alert']['service'], ['Flowtriq'])
        self.assertEqual(data['alert']['group'], 'DDoS')
        self.assertEqual(data['alert']['value'], '2.45M pps / 1.4 Gbps bps')
        self.assertEqual(data['alert']['text'],
                         'A large 1.4 Gbps UDP flood from 8,429 source IPs targeting web-prod-1')
        self.assertIn('ip=203.0.113.10', data['alert']['tags'])
        self.assertIn('family=udp_flood', data['alert']['tags'])
        self.assertIn('sources=8429', data['alert']['tags'])
        self.assertEqual(data['alert']['origin'], 'flowtriq/web-prod-1')
        self.assertEqual(data['alert']['attributes']['peakPps'], 2450000)
        self.assertEqual(data['alert']['attributes']['peakBps'], 1547000000)
        self.assertEqual(data['alert']['attributes']['sourceIpCount'], 8429)

    def test_flowtriq_attack_end(self):
        """Test DDoS attack resolved webhook."""

        attack_end = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_end",
            "timestamp": "2025-03-10T14:35:00Z",
            "incident": {
                "id": 147,
                "title": "UDP Flood on web-prod-1",
                "severity": "critical",
                "attack_family": "udp_flood",
                "peak_pps": 2450000,
                "peak_pps_fmt": "2.45M",
                "peak_bps": 1547000000,
                "peak_bps_fmt": "1.4 Gbps",
                "source_ip_count": 8429,
                "duration_seconds": 780,
                "duration_fmt": "13m 0s",
                "ai_summary": null,
                "status": "resolved",
                "started_at": "2025-03-10T14:22:00Z",
                "resolved_at": "2025-03-10T14:35:00Z",
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=147"
            },
            "node": {
                "name": "web-prod-1",
                "ip_address": "203.0.113.10"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=attack_end, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'web-prod-1')
        self.assertEqual(data['alert']['event'], 'DDoS_udp_flood')
        self.assertEqual(data['alert']['severity'], 'ok')
        self.assertEqual(data['alert']['status'], 'closed')
        self.assertEqual(data['alert']['text'],
                         'DDoS attack resolved on web-prod-1 after 13m 0s')
        self.assertEqual(data['alert']['attributes']['durationSeconds'], 780)
        self.assertEqual(data['alert']['attributes']['resolvedAt'],
                         '2025-03-10T14:35:00Z')

    def test_flowtriq_attack_update(self):
        """Test ongoing attack update webhook."""

        attack_update = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_update",
            "timestamp": "2025-03-10T14:28:00Z",
            "incident": {
                "id": 147,
                "title": "UDP Flood on web-prod-1",
                "severity": "high",
                "attack_family": "udp_flood",
                "peak_pps": 4800000,
                "peak_pps_fmt": "4.8M",
                "peak_bps": 3200000000,
                "peak_bps_fmt": "3.0 Gbps",
                "source_ip_count": 12500,
                "duration_seconds": 360,
                "duration_fmt": "6m 0s",
                "ai_summary": null,
                "description": "An ongoing attack has been updated on node web-prod-1. Type: udp_flood, Peak: 4.8M pps.",
                "status": "active",
                "started_at": "2025-03-10T14:22:00Z",
                "resolved_at": null,
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=147"
            },
            "node": {
                "name": "web-prod-1",
                "ip_address": "203.0.113.10"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=attack_update, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['severity'], 'major')
        self.assertEqual(data['alert']['value'], '4.8M pps / 3.0 Gbps bps')
        self.assertEqual(data['alert']['attributes']['peakPps'], 4800000)

    def test_flowtriq_test_event(self):
        """Test webhook test event."""

        test_event = r"""
        {
            "source": "flowtriq",
            "event_type": "test",
            "severity": "medium",
            "title": "Test Notification",
            "description": "This is a test notification from Flowtriq."
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=test_event, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'flowtriq')
        self.assertEqual(data['alert']['event'], 'FlowtriqTest')
        self.assertEqual(data['alert']['severity'], 'informational')
        self.assertEqual(data['alert']['text'],
                         'This is a test notification from Flowtriq.')

    def test_flowtriq_syn_flood(self):
        """Test SYN flood attack type."""

        syn_flood = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_start",
            "timestamp": "2025-03-15T08:00:00Z",
            "incident": {
                "id": 200,
                "title": "SYN Flood on edge-router-1",
                "severity": "high",
                "attack_family": "syn_flood",
                "peak_pps": 950000,
                "peak_pps_fmt": "950K",
                "peak_bps": 450000000,
                "peak_bps_fmt": "430 Mbps",
                "source_ip_count": 3200,
                "duration_seconds": 0,
                "duration_fmt": "",
                "ai_summary": null,
                "status": "active",
                "started_at": "2025-03-15T08:00:00Z",
                "resolved_at": null,
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=200"
            },
            "node": {
                "name": "edge-router-1",
                "ip_address": "198.51.100.5"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=syn_flood, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'edge-router-1')
        self.assertEqual(data['alert']['event'], 'DDoS_syn_flood')
        self.assertEqual(data['alert']['severity'], 'major')
        self.assertEqual(data['alert']['correlate'], ['DDoS_syn_flood'])
        self.assertIn('ip=198.51.100.5', data['alert']['tags'])

    def test_flowtriq_custom_environment(self):
        """Test custom environment via query string."""

        attack_start = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_start",
            "timestamp": "2025-03-10T14:22:00Z",
            "incident": {
                "id": 300,
                "title": "DNS Amplification on staging-1",
                "severity": "medium",
                "attack_family": "dns_amplification",
                "peak_pps": 500000,
                "peak_pps_fmt": "500K",
                "peak_bps": 200000000,
                "peak_bps_fmt": "190 Mbps",
                "source_ip_count": 1200,
                "duration_seconds": 0,
                "duration_fmt": "",
                "ai_summary": null,
                "status": "active",
                "started_at": "2025-03-10T14:22:00Z",
                "resolved_at": null,
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=300"
            },
            "node": {
                "name": "staging-1",
                "ip_address": "10.0.0.50"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq?environment=Staging',
            data=attack_start, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['environment'], 'Staging')

    def test_flowtriq_service_port_detection(self):
        """Test Service Port detection fields are included."""

        sp_attack = r"""
        {
            "source": "flowtriq",
            "event_type": "attack_start",
            "timestamp": "2025-06-03T10:00:00Z",
            "incident": {
                "id": 400,
                "title": "UDP Flood on game-server-1",
                "severity": "critical",
                "attack_family": "udp_flood",
                "peak_pps": 5000000,
                "peak_pps_fmt": "5M",
                "peak_bps": 2000000000,
                "peak_bps_fmt": "1.9 Gbps",
                "source_ip_count": 15000,
                "duration_seconds": 0,
                "duration_fmt": "",
                "ai_summary": null,
                "status": "active",
                "started_at": "2025-06-03T10:00:00Z",
                "resolved_at": null,
                "dashboard_url": "https://flowtriq.com/dashboard/incident?id=400",
                "sp_zone": "non_service",
                "sp_service_pps": 200,
                "sp_non_service_pps": 4999800,
                "sp_blocks_deployed": 3
            },
            "node": {
                "name": "game-server-1",
                "ip_address": "192.0.2.100"
            }
        }
        """

        response = self.client.post(
            '/webhooks/flowtriq', data=sp_attack, content_type='application/json')

        self.assertEqual(response.status_code, 201, response.data)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['attributes']['spZone'], 'non_service')
        self.assertEqual(data['alert']['attributes']['spBlocksDeployed'], 3)

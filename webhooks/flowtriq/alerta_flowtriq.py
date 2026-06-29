import hashlib
import hmac
import os
from datetime import datetime
from typing import Any, Dict

from flask import request

from alerta.exceptions import RejectException
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase

JSON = Dict[str, Any]

SEVERITY_MAP = {
    'critical': 'critical',
    'high': 'major',
    'medium': 'warning',
    'low': 'minor',
}

EVENT_TYPE_MAP = {
    'attack_start': 'open',
    'attack_update': 'open',
    'attack_end': 'closed',
    'test': 'open',
}


class FlowtriqWebhook(WebhookBase):
    """
    Flowtriq DDoS detection webhook receiver
    See https://flowtriq.com/docs?section=webhooks
    """

    def incoming(self, query_string, payload):

        # Verify HMAC-SHA256 signature if a secret is configured
        secret = os.environ.get('FLOWTRIQ_WEBHOOK_SECRET')
        if secret:
            signature = request.headers.get('X-Flowtriq-Signature', '')
            body = request.get_data(as_text=True)
            expected = 'sha256=' + hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, signature):
                raise RejectException('Invalid Flowtriq webhook signature')

        # Handle test events
        if payload.get('event_type') == 'test':
            return Alert(
                resource='flowtriq',
                event='FlowtriqTest',
                environment=query_string.get('environment', 'Production'),
                severity='informational',
                service=['Flowtriq'],
                group='DDoS',
                value='test',
                text=payload.get('description', 'Test notification from Flowtriq'),
                origin='flowtriq',
                event_type='flowtriqAlert',
                raw_data=str(payload)
            )

        incident = payload.get('incident', {})
        node = payload.get('node', {})
        event_type = payload.get('event_type', 'attack_start')

        if not incident:
            raise ValueError('No incident data in Flowtriq webhook payload')

        # Map Flowtriq severity to alerta severity
        flowtriq_severity = incident.get('severity', 'medium')
        if event_type == 'attack_end':
            severity = 'ok'
        else:
            severity = SEVERITY_MAP.get(flowtriq_severity, 'warning')

        # Build resource identifier from node info
        node_name = node.get('name', 'unknown')
        node_ip = node.get('ip_address', '')
        resource = node_name if node_name != 'unknown' else node_ip or 'flowtriq'

        # Build event name from attack family
        attack_family = incident.get('attack_family', 'DDoS')
        event = 'DDoS_{}'.format(attack_family)

        # Build descriptive text
        peak_pps_fmt = incident.get('peak_pps_fmt', str(incident.get('peak_pps', 0)))
        peak_bps_fmt = incident.get('peak_bps_fmt', str(incident.get('peak_bps', 0)))
        source_count = incident.get('source_ip_count', 0)

        if event_type == 'attack_end':
            duration_fmt = incident.get('duration_fmt', '')
            text = 'DDoS attack resolved on {}'.format(node_name)
            if duration_fmt:
                text += ' after {}'.format(duration_fmt)
        else:
            text = incident.get('ai_summary') or incident.get('description') or \
                '{} attack on {} - Peak: {} pps / {} bps from {} sources'.format(
                    attack_family.replace('_', ' ').title(),
                    node_name,
                    peak_pps_fmt,
                    peak_bps_fmt,
                    source_count
                )

        # Build value string
        value = '{} pps / {} bps'.format(peak_pps_fmt, peak_bps_fmt)

        # Build tags
        tags = []
        if node_ip:
            tags.append('ip={}'.format(node_ip))
        if incident.get('attack_family'):
            tags.append('family={}'.format(incident['attack_family']))
        if source_count:
            tags.append('sources={}'.format(source_count))

        # Correlate start/update/end events for the same incident
        correlate = ['DDoS_{}'.format(attack_family)]

        # Build attributes
        attributes = {
            'flowtriqEventType': event_type,
            'peakPps': incident.get('peak_pps', 0),
            'peakBps': incident.get('peak_bps', 0),
            'sourceIpCount': source_count,
        }

        if incident.get('dashboard_url'):
            attributes['moreInfo'] = '<a href="{}" target="_blank">Flowtriq Dashboard</a>'.format(
                incident['dashboard_url'])

        if incident.get('ai_summary'):
            attributes['aiSummary'] = incident['ai_summary']

        if incident.get('duration_seconds'):
            attributes['durationSeconds'] = incident['duration_seconds']

        if incident.get('started_at'):
            attributes['startedAt'] = incident['started_at']

        if incident.get('resolved_at'):
            attributes['resolvedAt'] = incident['resolved_at']

        # Service Port detection fields
        if incident.get('sp_zone'):
            attributes['spZone'] = incident['sp_zone']
        if incident.get('sp_blocks_deployed'):
            attributes['spBlocksDeployed'] = incident['sp_blocks_deployed']

        # Parse create_time
        create_time = None
        ts = payload.get('timestamp') or incident.get('started_at')
        if ts:
            for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S%z'):
                try:
                    create_time = datetime.strptime(ts, fmt)
                    break
                except ValueError:
                    continue

        return Alert(
            resource=resource,
            event=event,
            environment=query_string.get('environment', 'Production'),
            severity=severity,
            correlate=correlate,
            service=['Flowtriq'],
            group='DDoS',
            value=value,
            text=text,
            tags=tags,
            attributes=attributes,
            origin='flowtriq/{}'.format(node_name),
            event_type='flowtriqAlert',
            create_time=create_time,
            raw_data=str(payload)
        )

import traceback
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json
import sys

class ObserviumWebhook(WebhookBase):
    """
    Observium Network Monitoring
    Implementation by Extreme Labs
    """
    def incoming(self, query_string, payload, path=None):
        try:
            return Alert(
                resource=payload['DEVICE_HOSTNAME'],
                event=payload['ALERT_MESSAGE'],
                event_type=payload['ALERT_STATE'],
                environment='Production',
                service=['network'],
                severity=payload['ALERT_SEVERITY'].lower(),
                value=payload['DEVICE_LOCATION'],
                text=payload['TITLE'],
                attributes={},
                origin='Observium',
                raw_data=json.dumps(payload))
        except Exception as e:
            return Alert(
                resource='Alerta Observium integration',
                event='Webhook Failure',
                event_type='Python Exception',
                environment='Production',
                service=['alerta','webhook','observium'],
                severity='critical',
                value=str(type(e)),
                text='Webhook failed',
                attributes={},
                origin='Alerta Observium Webhook',
                raw_data=json.dumps({
                    'payload': payload,
                    'query_string': query_string,
                    'path': path,
                    'traceback': traceback.format_exc()
                })
            )
            
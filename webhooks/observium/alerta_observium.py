from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json

class ObserviumWebhook(WebhookBase):
    """
    Observium Network Monitoring
    Implementation by Extreme Labs
    """
    def incoming(self, query_string, payload, path=None):

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
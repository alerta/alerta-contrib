import json

from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class MailgunWebhook(WebhookBase):

    def incoming(self, query_string, payload):

        # Load variables from querystring
        try:
            environment = query_string['environment']
        except Exception:
            environment = 'Production'
        try:
            severity = query_string['severity']
        except Exception:
            severity = 'major'
        try:
            group = query_string['group']
        except Exception:
            group = 'Email'

        return Alert(
            resource=payload['sender'],
            type='Email Alert',
            event=payload['subject'],
            environment=environment,
            severity=severity,
            service=['Email'],
            group=group,
            text=payload['stripped-text'] or payload['body-plain'],
            tags=[],
            attributes={},
            origin='Mailgun/{}'.format(payload['recipient']),
            raw_data=json.dumps(payload, indent=4)
        )

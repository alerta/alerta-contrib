
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json
import datetime


class MailgunWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        
        # Load variables from querystring
        try:
            environment = query_string['environment']
        except:
            environment = 'Production'
        try:
            create_time = datetime.datetime.fromtimestamp(int(payload['timestamp'])).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            create_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        try:
            severity = query_string['severity']
        except:
            severity = 'major'
        try:
            group = query_string['group']
        except:
            group = 'Email'

        return Alert(
            resource=payload['sender'],
            create_time=create_time,
            type='Email Alert',
            event=payload['subject'],
            environment=environment,
            severity=severity,
            service=['Email'],
            group=group,
            text=payload['stripped-text'],
            tags=[],
            attributes={},
            origin='Mailgun/{}'.format(payload['recipient']),
            raw_data=json.dumps(payload, indent=4)
        )


from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json

class Fail2BanWebhook(WebhookBase):

    def incoming(self, query_string, payload):

        # Default parameters
        environment = 'Production'
        severity ='security'
        group ='Fail2Ban'
        text = ''
        tags = []
        attributes = {}
        origin = ''

        return Alert(
            resource=payload['resource'],
            event=payload['event'],
            environment=payload.get('environment', environment),
            severity=payload.get('severity', severity),
            service=['fail2ban'],
            group=payload.get('group', group),
            value='BAN',
            text=payload.get('message', text),
            tags=payload.get('tags', tags),
            attributes=payload.get('attributes', attributes),
            origin=payload.get('hostname', origin),
            raw_data=json.dumps(payload, indent=4)
        )

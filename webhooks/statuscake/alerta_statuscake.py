import hashlib
import os

from alerta.exceptions import RejectException
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class StatusCakeWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        alert_severity = os.environ.get(
            'STATUSCAKE_DEFAULT_ALERT_SEVERITY', 'major')

        # If the statuscake username and apikey are provided  # noqa: E265
        # We can validate that the webhook call is valid
        statuscake_username = os.environ.get('STATUSCAKE_USERNAME')
        statuscake_apikey = os.environ.get('STATUSCAKE_APIKEY')

        if statuscake_username and statuscake_apikey:
            decoded_token = statuscake_username + statuscake_apikey
            statuscake_token = hashlib.md5(decoded_token.encode()).hexdigest()
            if statuscake_token != payload['Token']:
                raise RejectException("Provided Token couldn't be verified")

        if payload['Status'] == 'UP':
            severity = 'normal'
        else:
            severity = alert_severity

        return Alert(
            resource=payload['Name'],
            event='AppDown',
            environment='Production',
            severity=severity,
            service=['StatusCake'],
            group='Application',
            value=payload['StatusCode'],
            text='%s is down' % payload['URL'],
            tags=payload['Tags'].split(','),
            origin='statuscake',
            raw_data=str(payload)
        )

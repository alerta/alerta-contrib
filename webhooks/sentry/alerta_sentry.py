
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class SentryWebhook(WebhookBase):

    def incoming(self, query_string, payload):

        # For Sentry v9
        # Defaults to value before Sentry v9
        if 'request' in payload['data'].get('event'):
            key = 'request'
        else:
            key = 'sentry.interfaces.Http'

        if payload['data'].get('event')[key]['env']['ENV'] == 'prod':
            environment = 'Production'
        else:
            environment = 'Development'

        if payload['data']['level'] == 'error':
            severity = 'critical'
        else:
            severity = 'ok'

        return Alert(
            resource=payload['data']['culprit'],
            event=payload['data']['event']['event_id'],
            environment=environment,
            severity=severity,
            service=[payload['data']['project']],
            group='Application',
            value=payload['data']['level'],
            text='{} {}'.format(payload['data']['message'], payload['data']['url']),
            tags=['{}={}'.format(k, v) for k, v in payload['data']['event']['tags']],
            attributes={'modules': ['{}=={}'.format(k, v) for k, v in payload['data']['event']['modules'].items()]},
            origin='sentry.io',
            raw_data=str(payload)
        )

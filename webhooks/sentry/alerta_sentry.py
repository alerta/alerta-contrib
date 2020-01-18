
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class SentryWebhook(WebhookBase):

    def incoming(self, query_string, payload):

        if payload.get('event')['sentry.interfaces.Http']['env']['ENV'] == 'prod':
            environment = 'Production'
        else:
            environment = 'Development'

        if payload['level'] == 'error':
            severity = 'critical'
        else:
            severity = 'ok'

        return Alert(
            resource=payload['culprit'],
            event=payload['event']['event_id'],
            environment=environment,
            severity=severity,
            service=[payload['project']],
            group='Application',
            value=payload['level'],
            text='{} {}'.format(payload['message'], payload['url']),
            tags=['{}={}'.format(k, v) for k, v in payload['event']['tags']],
            attributes={'modules': ['{}=={}'.format(k, v) for k, v in payload['event']['modules'].items()]},
            origin='sentry.io',
            raw_data=str(payload)
        )

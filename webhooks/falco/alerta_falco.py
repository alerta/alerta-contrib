from flask import current_app
from alerta.app import alarm_model
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class FalcoWebhook(WebhookBase):
    """
    Falco webhook
    """

    def incoming(self, query_string, payload):

        additional_tags = []
        additional_attributes = {}

        # checking fields
        #
        expected_fields = [
            'priority',
            'hostname',
            'rule',
            'output_fields',
            'source',
            'output'
        ]
        for field in expected_fields:
            if field not in payload:
                raise Exception(f'{field} not found in payload')
        expected_fields_in_outputfields = ['environment']
        for field in expected_fields_in_outputfields:
            if field not in payload['output_fields']:
                raise Exception(f'{field} not found in payload->output_fields')

        # resource+event
        #
        # these are the fields used for de duplication,
        # so we fill their values here
        resource = f"{payload['hostname']}"
        event = payload['rule']

        # priority
        #
        # falco priorities:
        # emergency, alert, critical, error, warning, notice,
        # informational, debug
        if payload['priority'].lower() in [
                'emergency',
                'alert',
                'critical',
                'error'
        ]:
            severity = 'critical'
        elif payload['priority'].lower() in [
                'warning',
                'notice',
                'informational',
                'debug'
        ]:
            severity = 'warning'
        else:
            severity = alarm_model.DEFAULT_NORMAL_SEVERITY
        additional_attributes['falco_priority'] = payload['priority']

        # environment
        #
        # we set a custom field environment in our setup
        environment = current_app.config['DEFAULT_ENVIRONMENT']
        if 'output_fields' in payload and 'environment' in payload['output_fields']:
            environment = payload['output_fields']['environment']

        # attributes
        #
        attributes = additional_attributes

        # tags
        tags = []
        if 'tags' in payload and isinstance(payload['tags'], list):
            tags = additional_tags.extend(payload['tags'])
        else:
            tags = additional_tags

        # group
        #
        # how to group
        group = f"{payload['rule']}-{payload['source']}"

        # value
        #
        value = payload['output']

        # service
        #
        # service is a List
        service = [payload['source']]

        # origin
        #
        origin = f"{payload['hostname']}-{payload['source']}"

        # event type
        #
        # in this case is a Falco Alert
        event_type = 'falcoAlert'

        # text
        #
        # the alert text
        text = f"{severity}: {payload['output_fields']}"

        return Alert(
            # alerta will group by these
            resource=resource,
            event=event,
            # ################
            environment=environment,
            severity=severity,
            service=service,
            group=group,
            value=value,
            text=text,
            tags=tags,
            origin=origin,
            attributes=attributes,
            event_type=event_type,
            raw_data=payload
            )

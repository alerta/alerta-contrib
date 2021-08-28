
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class QueryWebhook(WebhookBase):

    def incoming(self, query_string, payload):

        # Load variables from querystring
		# resource
        try:
            resource = query_string['resource']
        except:
            resource = 'QueryDefaultResource'
		# environment
        try:
            environment = query_string['environment']
        except:
            environment = 'Production'
		# severity
        try:
            severity = query_string['severity']
        except:
            severity = 'major'
		# group
        try:
            group = query_string['group']
        except:
            group = 'QueryDefaultGroup'
		# event
        try:
            event = query_string['event']
        except:
            event = 'QueryDefaultEvent'
		# service (Must be an array)
        try:
            service = [query_string['service']]
        except:
            service = ['QueryDefaultService']
		# value
        try:
            value = query_string['value']
        except:
            value = ''
		# text
        try:
            text = query_string['text']
        except:
            text = ''
		# tags (Must be an array)
        try:
            tags = query_string['tags'].split(',')
        except:
            tags = []
		# origin
        try:
            origin = query_string['origin']
        except:
            origin = 'QueryDefaultOrigin'
		# timeout
        try:
            timeout = int(query_string['timeout'])
        except:
            timeout = 86400

        return Alert(
            resource=resource,
            event=event,
            environment=environment,
            severity=severity,
            service=service,
            group=group,
            value=value,
            text=text,
            tags=tags,
            origin=origin,
			timeout=timeout,
            raw_data=query_string
        )

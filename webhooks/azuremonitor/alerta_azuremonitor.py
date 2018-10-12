from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json

class AzureMonitorWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        
        # fail-safe to a default environment
        try:
            environment = query_string['environment']
        except:
            environment = 'Production'
        
        # Azure has two formats for their webhooks (the first one is new format and the second one is old format)
        try:
            if payload['data']['status'] == 'Activated':
                severity = 'critical'
            elif payload['data']['status'] == 'Resolved':
                severity = 'ok'
            else:
                severity = 'unknown'
                
            resource        = payload['data']['context']['resourceName']
            create_time     = payload['data']['context']['timestamp']
            event           = payload['data']['context']['name']
            service         = payload['data']['context']['resourceType']
            group           = payload['data']['context']['resourceGroupName']
            tags            = ['{}={}'.format(k, v) for k, v in payload['data']['properties'].items()]

            if payload['schemaId'] == 'AzureMonitorMetricAlert':
                event_type = 'MetricAlert'
                text = '{}: {} {} ({} {})'.format(severity.upper(), payload['data']['context']['condition']['allOf'][0]['metricValue'], payload['data']['context']['condition']['allOf'][0]['metricName'], payload['data']['context']['condition']['allOf'][0]['operator'], payload['data']['context']['condition']['allOf'][0]['threshold'])
                value = '{} {}'.format(payload['data']['context']['condition']['allOf'][0]['metricValue'], payload['data']['context']['condition']['allOf'][0]['metricName'])
            else:
                text = '{}'.format(severity.upper())
                value = ''
                event_type = 'EventAlert'
        
        except:
            if payload['status'] == 'Activated':
                severity = 'critical'
            elif payload['status'] == 'Resolved':
                severity = 'ok'
            else:
                severity = 'unknown'
    
            if payload['context']['conditionType'] == 'Metric':
                text = '{}: {} {} ({} {})'.format(severity.upper(), payload['context']['condition']['metricValue'], payload['context']['condition']['metricName'], payload['context']['condition']['operator'], payload['context']['condition']['threshold'])
                value = '{} {}'.format(payload['context']['condition']['metricValue'], payload['context']['condition']['metricName'])
            else:
                text = '{}'.format(severity.upper())
                value = ''
            
            resource        = payload['context']['resourceName']
            create_time     = payload['context']['timestamp']
            event_type      = '{}Alert'.format(payload['context']['conditionType'])
            event           = payload['context']['name']
            service         = [payload['context']['resourceType']]
            group           = payload['context']['resourceGroupName']
            tags            = ['{}={}'.format(k, v) for k, v in payload['properties'].items()]

        return Alert(
            resource=resource,
            create_time=create_time,
            type=event_type,
            event=event,
            environment=environment,
            severity=severity,
            service=service,
            group=group,
            value=value,
            text=text,
            tags=tags,
            attributes={},
            origin='Azure Monitor',
            raw_data=json.dumps(payload, indent=4)
        )

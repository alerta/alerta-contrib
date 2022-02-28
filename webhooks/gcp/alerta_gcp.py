from flask import request
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import os
import logging

LOG = logging.getLogger('alerta.webhooks.gcp')

class GoogleCloudPlatformWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        gcp_alert = payload['incident']

        if gcp_alert['state'].lower() == 'closed':
            severity = 'normal'
        else:
            severity = os.environ.get('GCP_DEFAULT_ALERT_SEVERITY', 'warning')

        value = "N/A"
        try:
            value = gcp_alert['observed_value']
        except:
            LOG.error("Unable to real alert observed_value")

        attributes = {
            "incident-id": gcp_alert.get('incident_id'),
            "documenation": gcp_alert.get('documentation'),
            "Source Alert": gcp_alert.get('url')
        }

        return Alert(
            resource=gcp_alert.get('resource_display_name','N/A'),
            event=gcp_alert.get('policy_name','GCPEvent'),
            environment='Production',
            severity=severity,
            service=['GCP'],
            group='Cloud',
            value=value,
            text=gcp_alert.get('summary', 'Something happened in GCP'),
            origin='gcp',
            attributes=attributes,
            raw_data=str(payload)
        )

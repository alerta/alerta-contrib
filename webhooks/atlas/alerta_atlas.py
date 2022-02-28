from flask import request
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
from alerta.exceptions import RejectException
import os
from hashlib import sha1
import hmac
import logging
from base64 import b64decode

LOG = logging.getLogger('alerta.webhooks.atlas')

class MongodbAtlasWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        atlas_alert = payload

        # If the webhook secret is provider,
        # We can validate that the webhook call is valid
        atlas_secret = os.environ.get('MONGODB_ATLAS_VALIDATION_SECRET')

        decoded_received_signature = b64decode(request.headers.get('X-MMS-Signature'))

        if atlas_secret:
            signed_body = hmac.new(atlas_secret.encode('utf-8'), request.get_data(), sha1).digest()
            LOG.info(signed_body)
            if not hmac.compare_digest(signed_body, decoded_received_signature):
                raise RejectException("Webhook signature doesn't match")

        if atlas_alert['status'] == 'OPEN':
            if request.headers.get('X-MMS-Event') == 'alert.inform':
                severity = "informational"
            else:
                severity = os.environ.get('MONGODB_ATLAS_DEFAULT_ALERT_SEVERITY', 'warning')
        else:
            severity = 'normal'

        value = "N/A"
        try:
            if 'number' in atlas_alert['currentValue']:
                value = round(atlas_alert['currentValue']['number'],2)
        except:
            LOG.error("Unable to real alert currentValue")

        attributes = {
            "group-id": atlas_alert.get('groupId'),
            "metric-type": atlas_alert.get('typeName'),
            "host": atlas_alert.get('hostnameAndPort'),
            "Full Text": atlas_alert.get('humanReadable'),
            "Source Alert": "<a href=https://cloud.mongodb.com/api/atlas/v1.0/groups/%s/alerts/%s>%s</a>" % (atlas_alert.get('groupId'), atlas_alert.get('id'), atlas_alert.get('id'))
        }

        event = 'AtlasEvent'
        if atlas_alert.get('typeName') == "HOST_METRIC":
            event = atlas_alert.get('metricName','AtlasEvent')
        elif atlas_alert.get('typeName') == "HOST":
            event = atlas_alert.get('eventTypeName','AtlasEvent')

        return Alert(
            resource=atlas_alert['clusterName'],
            event=event,
            environment='Production',
            severity=severity,
            service=['MongoDBAtlas'],
            group='Databases',
            value=value,
            text="Cluster %s triggered %s" % (atlas_alert['clusterName'], event),
            origin='mongodb-atlas',
            attributes=attributes,
            raw_data=str(payload)
        )

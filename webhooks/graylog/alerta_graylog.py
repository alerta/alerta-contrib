from pprint import pprint
import traceback
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json

# alarm duplication - event, resource, environment, severity(colleration)


class GraylogWebhook(WebhookBase):
    """
    Graylog Monitoring
    Implementation by Extreme Labs
    """

    def incoming(self, query_string, payload, path=None):
        try:
            return Alert(
                resource=payload["backlog"][0]["source"],
                text=payload["event"]["message"],
                # event_type=payload["event"]["event_definition_type"],
                environment=query_string.get("environment", "Production"),
                service=["Graylog"],
                severity=query_string.get("severity", "warning"),
                # value=payload["TITLE"],
                event=payload["backlog"][0]["message"],
                # attributes={
                #     "Device URL": payload["DEVICE_URL"],
                #     "Entity Description": payload["ENTITY_DESCRIPTION"],
                #   "Device Locaiton": f"Facility {payload['backlog']['fields']['facility']} number {payload['backlog']['fields']['facility_num']}",
                #     "Entity Type": payload["ENTITY_TYPE"],
                #     "Device Hardware": payload["DEVICE_HARDWARE"],
                #     "Device Uptime": payload["DEVICE_UPTIME"],
                # },
                # group=payload["DEVICE_LOCATION"],
                origin=payload["event"]["source"],
                raw_data=json.dumps(payload),
            )
        except Exception as e:
            return Alert(
                resource="Alerta Graylog integration",
                event="Webhook Failure",
                event_type="Python Exception",
                environment="Production",
                service=["alerta", "webhook", "graylog"],
                severity="critical",
                value=str(type(e)),
                text="Webhook failed",
                attributes={},
                origin="Alerta Graylog Webhook",
                raw_data=json.dumps(
                    {
                        "payload": payload,
                        "query_string": query_string,
                        "path": path,
                        "traceback": traceback.format_exc(),
                    }
                ),
            )

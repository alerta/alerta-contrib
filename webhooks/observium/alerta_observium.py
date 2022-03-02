import json
import traceback
from typing import Any, Dict

from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class ObserviumWebhook(WebhookBase):
    """
    Observium Network Monitoring
    Implementation by Extreme Labs
    """

    def incoming(self, query_string, payload: Dict[str, Any], path=None):
        try:
            return Alert(
                resource=payload["DEVICE_HOSTNAME"],
                event=payload["ENTITY_NAME"],
                event_type=payload["ALERT_STATE"],
                environment="Production",
                service=["network"],
                severity=(
                    "normal"
                    if payload.get("ALERT_STATE", False) == "RECOVER"
                    else payload["ALERT_SEVERITY"].lower()
                ),
                value=payload["ENTITY_DESCRIPTION"],
                text=payload["ALERT_MESSAGE"],
                attributes={
                    "Device URL": payload["DEVICE_URL"],
                    "Entity Description": payload["ENTITY_DESCRIPTION"],
                    "Device Location": payload["DEVICE_LOCATION"],
                    "Entity Type": payload["ENTITY_TYPE"],
                    "Device Hardware": payload["DEVICE_HARDWARE"],
                    "Device Uptime": payload["DEVICE_UPTIME"],
                },
                group=payload["DEVICE_LOCATION"],
                origin="Observium",
                raw_data=json.dumps(
                    payload,
                    indent=4,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        except Exception as e:
            return Alert(
                resource="Alerta Observium integration",
                event="Webhook Failure",
                event_type="Python Exception",
                environment="Production",
                service=["alerta", "webhook", "observium"],
                severity="critical",
                value=str(type(e)),
                text="Webhook failed",
                attributes={},
                origin="Alerta Observium Webhook",
                raw_data=json.dumps(
                    {
                        "payload": payload,
                        "query_string": query_string,
                        "path": path,
                        "traceback": traceback.format_exc(),
                    },
                    sort_keys=True,
                    indent=4,
                    separators=(",", ":"),
                ),
            )

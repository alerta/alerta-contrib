import json
import traceback
from typing import Any, Dict

from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase


class XnmsWebhook(WebhookBase):
    """
    x3me Network Monitoring System
    """

    def incoming(self, query_string: str, payload: Dict[str, Any], path=None):
        try:
            return Alert(
                **{
                    **payload,
                    "attributes": {
                        f"xNMS {k}": v
                        for k, v in json.loads(payload["attributes"]).items()
                    }
                    if payload.get("attributes")
                    else None,
                    "raw_data": json.dumps(
                        payload,
                        sort_keys=True,
                        indent=4,
                    ),
                },
            )
        except Exception as e:
            return Alert(
                resource="Alerta xNMS integration",
                event="Webhook Failure",
                event_type="Python Exception",
                environment="Production",
                service=["alerta", "webhook", "xnms"],
                severity="critical",
                value=str(type(e)),
                text="Webhook failed",
                origin="Alerta xNMS Webhook",
                raw_data=json.dumps(
                    {
                        "payload": payload,
                        "query_string": query_string,
                        "path": path,
                        "traceback": traceback.format_exc(),
                    },
                    sort_keys=True,
                    indent=4,
                ),
            )

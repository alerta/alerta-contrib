import traceback
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json


class XnmsWebhook(WebhookBase):
    """
    x3me Network Monitoring System
    """

    def incoming(self, query_string, payload, path=None):
        try:
            return Alert(**payload)
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
                attributes={},
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
                    separators=(',',':')
                ),
            )

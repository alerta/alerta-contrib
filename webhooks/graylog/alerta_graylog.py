import traceback
from typing import Dict, List
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase
import json


def parse_syslog_snmp_trap(msg: str) -> Dict[str, any]:
    boundaries = [" ", ",", ".", "(", ")", "="]
    quotechar = '"'

    kvsep = "="
    res = dict()

    idx = msg.find(kvsep)

    # If no separator is found, return unmodified message
    if idx == -1:
        raise ValueError("No key-value pairs found in message")

    # Validate quoted values
    if msg.count(quotechar) % 2 != 0:
        print("Mismatched quotes")
        raise SyntaxError("Mismatched quotes in message")

    while idx > -1:
        # Get the key
        key = ""
        for charidx in reversed(range(idx)):
            if msg[charidx] == quotechar:
                start = msg.rfind(quotechar, end=charidx)
                if start > -1:
                    key = msg[start:charidx]
                break
            if msg[charidx] in boundaries:
                break
            key = msg[charidx] + key

        # Get the value
        value = ""
        for charidx in range(idx + 1, len(msg)):
            if msg[charidx] == quotechar:
                end = msg.find(quotechar, charidx + 1)
                if end > -1:
                    value = msg[charidx + 1 : end]
                    break
            if msg[charidx] in boundaries:
                break
            value += msg[charidx]

        if key and value:
            res[key] = value

        idx = msg.find(kvsep, idx + 1)

    return res


# alarm duplication - event, resource, environment, severity (corellation)
class GraylogWebhook(WebhookBase):
    """
    Graylog Monitoring
    Implementation by Extreme Labs
    """

    def incoming(self, query_string, payload, path=None):
        resource: str
        event: str
        text: str
        value: str = ""
        service: List[str] = ["graylog"]
        severity: str = query_string.get("severity", "warning")
        environment: str = query_string.get("environment", "Production")
        origin: str = payload["event"].get("source", "Graylog server")
        raw_data: str = json.dumps(payload)

        if not len(payload.get("backlog", [])):
            resource = origin
            event = f"Incorrect configuration for {payload['event']['message']}"
            text = "No messages were included in this alert, please enable the backlog parameter of the graylog alert definition!"
        else:
            resource = payload["backlog"][0]["source"]
            text = payload["event"]["message"]
            msg = payload["backlog"][0]["message"]

            try:
                data = parse_syslog_snmp_trap(msg)

                # Horrible way to do detection, not sure if there's a cleaner one right now
                if "RelativeResource" in data and "ReasonDescription" in data:
                    text = data["RelativeResource"]
                    value = data["ReasonDescription"]

                elif "MacAddress" in data:
                    text = data["MacAddress"]
                    value = f"MAC flapping on VLAN {data['VLANID']} between {data['Original-Port']} and {data['port']}"
                else:
                    # Parsed successfully, but we don't understand the data, so we default to the entire message in the description
                    text = msg

            except (SyntaxError, ValueError):
                event = payload["backload"][0]["message"]
                text = payload["event"]["message"]

        try:
            return Alert(
                resource=resource,
                text=text,
                environment=environment,
                service=service,
                severity=severity,
                event=event,
                origin=origin,
                raw_data=raw_data,
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

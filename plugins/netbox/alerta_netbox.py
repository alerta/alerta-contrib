import logging
from os import environ
from typing import Any, Callable, Dict, List, MutableMapping, Tuple
from urllib.parse import urljoin

import requests
from alerta.models.alert import Alert
from alerta.plugins import PluginBase

LOG = logging.getLogger("alerta.plugins.netbox")

GQL_QUERY = """query FindDevice($q: String) {{
    device_list(q: $q) {{
        id
        {fields}
    }}
}}"""

DEFAULT_FIELDS = "site { name, region { name } }, tenant { name }, custom_fields"


def flatten(d: MutableMapping, parent_key: str = "", sep: str = "_"):
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class NetboxEnhance(PluginBase):
    """
    Enhancing alerts with Netbox data.
    Implementation by Extreme Labs
    """

    def pre_receive(self, alert: Alert, **kwargs):
        NETBOX_URL = environ.get("NETBOX_URL") or kwargs["config"]["NETBOX_URL"]
        NETBOX_TOKEN = environ.get("NETBOX_TOKEN") or kwargs["config"]["NETBOX_TOKEN"]
        NETBOX_FIELDS = (
            environ.get("NETBOX_FIELDS")
            or kwargs["config"].get("NETBOX_FIELDS")
            or DEFAULT_FIELDS
        )

        LOG.debug("Enhancing alert with Netbox data")
        res = requests.post(
            urljoin(NETBOX_URL, "/graphql/"),
            headers={
                "Authorization": f"Token {NETBOX_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "query": GQL_QUERY.format(fields=NETBOX_FIELDS),
                "variables": {"q": alert.resource},
            },
        )

        if not res.ok:
            LOG.error(f"Failed to query Netbox (code {res.status_code}): {res.text}")
            return alert

        try:
            body = res.json()
        except ValueError:
            LOG.error("Failed to parse response body:", res.text)
            return alert

        if "error" in body or len(body["data"]["device_list"]) == 0:
            LOG.error("Request error:", body)
            return alert

        device: Dict = body["data"]["device_list"][0]
        device.update(device.pop("custom_fields", {}))
        device = flatten(device, sep=" ")

        device_url = f"{NETBOX_URL}/dcim/devices/{device.pop('id')}"
        device["url"] = f"<a href='{device_url}' target='_blank'>{device_url}</a>"

        trasnform_key: Callable[[str], str] = (
            lambda x: x[:-4].replace("_", " ")
            if x.endswith("name") and x != "name"
            else x
        )
        alert.attributes.update(
            {
                f"Netbox {trasnform_key(key)}".strip(): value
                for key, value in device.items()
            }
        )

        return alert

    def post_receive(self, alert: Alert):
        return

    def status_change(self, alert: Alert, status: str, text: str):
        return

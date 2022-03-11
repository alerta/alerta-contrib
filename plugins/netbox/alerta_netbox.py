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

DEFAULT_FIELDS = "site { name, region { name }, custom_fields }, tenant { name }, primary_ip4 { address }, custom_fields"


def squash_fields(obj: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    recurse = lambda x: squash_fields(x, fields) if isinstance(x, dict) else x
    newObj = dict()

    for key, value in obj.items():
        if key not in fields:
            newObj[key] = recurse(value)
            continue

        newObj.update(recurse(value))

    return newObj


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
            body: Dict[str, Any] = res.json()
        except ValueError:
            LOG.error(f"Failed to parse response body: {res.text}")
            return alert

        if "error" in body:
            LOG.error(f"Request error: {body}")
            return alert

        if not len(body["data"]["device_list"]):
            LOG.info(f"No devices found for {alert.resource}")
            return alert

        device: Dict[str, Any] = body["data"]["device_list"][0]
        device = squash_fields(device, ["custom_fields"])

        sep = " "
        device = flatten(device, sep=sep)

        device["url"] = f"{NETBOX_URL}/dcim/devices/{device.pop('id')}"
        device["ip"] = device.pop(
            f"primary_ip4{sep}address", device.pop(f"primary_ip6{sep}address", None)
        )

        transform_key: Callable[[str], str] = lambda x: (
            x[:-4] if x.endswith("name") and x != "name" else x
        ).replace("_", sep)

        alert.attributes.update(
            {
                f"Netbox {transform_key(key)}".strip(): value
                for key, value in device.items()
                if value
            }
        )

        if "xnms" in alert.service and device:
            alert.group = device.get(f"site{sep}region{sep}name", alert.group)

        return alert

    def post_receive(self, alert: Alert):
        return

    def status_change(self, alert: Alert, status: str, text: str):
        return

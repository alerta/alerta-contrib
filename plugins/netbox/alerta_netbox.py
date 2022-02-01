import logging
import os
from typing import Any, Dict, MutableMapping
from urllib.parse import urljoin

import requests
from alerta.models.alert import Alert
from alerta.plugins import PluginBase

LOG = logging.getLogger("alerta.plugins.netbox")

GQL_QUERY = """
query FindDevice($q: String) {
    device_list(q: $q) {
        id
        serial
        site {
            name
            region {
                name
            }
        }
        tenant {
            name
        }
    }
}
"""


def flatten(d: MutableMapping, parent_key="", sep="_"):
    items = []
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
        NETBOX_URL = os.environ.get("NETBOX_URL") or kwargs["config"]["NETBOX_URL"]
        NETBOX_TOKEN = (
            os.environ.get("NETBOX_TOKEN") or kwargs["config"]["NETBOX_TOKEN"]
        )

        LOG.debug("Enhancing alert with Netbox data")
        res = requests.post(
            urljoin(NETBOX_URL, "/graphql/"),
            headers={
                "Authorization": f"Token {NETBOX_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "query": GQL_QUERY,
                "variables": {"q": alert.resource},
            },
        )

        body = res.json()

        if "error" in body or len(body["data"]["device_list"]) == 0:
            LOG.error("Request error:", body)
            return alert

        device = flatten(body["data"]["device_list"][0], sep=" ")

        data: Dict[str, Any] = device | {
            "url": f"<a href='{NETBOX_URL}/dcim/devices/{device['id']}' target='_blank'>{alert.resource}</a>"
        }
        alert.attributes.update(
            {f"Netbox {key}": value for key, value in data.items() if key != "id"}
        )

        return alert

    def post_receive(self, alert: Alert):
        return

    def status_change(self, alert: Alert, status: str, text: str):
        return

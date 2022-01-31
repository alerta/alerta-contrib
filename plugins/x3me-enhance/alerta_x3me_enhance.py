import os
from typing import Any, Dict
from urllib.parse import urljoin

import requests
from alerta.plugins import PluginBase, app

GQL_QUERY = """
query FindDevice($q: String) {
  device_list(q: $q) {
    id
    name
  }
}
"""


NETBOX_URL = os.environ.get("NETBOX_URL") or app.config["NETBOX_URL"]
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN") or app.config["NETBOX_TOKEN"]


class EnhanceAlert(PluginBase):
    """
    Enhancing alerts with Netbox data.
    Implementation by Extreme Labs
    """

    def pre_receive(self, alert):

        res = requests.post(
            urljoin(NETBOX_URL, "/graphql/"),
            headers={
                "Authorization": f"Token {NETBOX_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "query": GQL_QUERY,
                "variables": {"q": alert["DEVICE_HOSTNAME"]},
            },
        )
        data: Dict[str, Any] = res.json()["data"]["device_list"][0]

        return {
            **alert,
            **{f"NETBOX_{key.upper()}": value for key, value in data.items()},
        }

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

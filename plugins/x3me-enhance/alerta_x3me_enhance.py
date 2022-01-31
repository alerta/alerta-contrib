import os
from typing import Any, Dict
from urllib.parse import urljoin

import requests
from alerta.models.alert import Alert
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

    def pre_receive(self, alert: Alert):

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
        data: Dict[str, Any] = res.json()["data"]["device_list"][0]
        alert.attributes.update(data)

        return alert

    def post_receive(self, alert: Alert):
        return

    def status_change(self, alert: Alert, status: str, text: str):
        return

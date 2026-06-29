Flowtriq Webhook
================

Receive [Flowtriq](https://flowtriq.com) DDoS detection alerts via webhook callbacks.

Flowtriq is a DDoS detection and traffic analysis platform. This webhook normalizes Flowtriq's incident alerts into Alerta's alert format so NOC teams can see DDoS events alongside all their other infrastructure alerts.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/flowtriq

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

The custom webhook will be auto-detected and added to the list of available API endpoints.

**1. In Flowtriq:** Go to Settings > Notification Channels > Add Channel > Webhook and set the URL to:

    https://your-alerta-server/api/webhooks/flowtriq

Optionally set a webhook secret to enable HMAC-SHA256 signature verification.

**2. In Alerta:** Optionally set the `FLOWTRIQ_WEBHOOK_SECRET` environment variable to verify incoming webhook signatures:

    export FLOWTRIQ_WEBHOOK_SECRET=your-secret-here

**3. Custom environment:** Append `?environment=YourEnv` to the webhook URL to override the default `Production` environment:

    https://your-alerta-server/api/webhooks/flowtriq?environment=Staging

Alert Mapping
-------------

| Flowtriq Field          | Alerta Field    |
|-------------------------|-----------------|
| `node.name`             | `resource`      |
| `incident.attack_family`| `event`         |
| `incident.severity`     | `severity`      |
| `incident.ai_summary`   | `text`          |
| `incident.peak_pps/bps` | `value`         |
| `event_type`            | correlate/status|
| `node.ip_address`       | `tags`          |

Severity mapping:

| Flowtriq  | Alerta          |
|-----------|-----------------|
| critical  | critical        |
| high      | major           |
| medium    | warning         |
| low       | minor           |
| (resolved)| ok              |

Example Payload
---------------

```json
{
  "source": "flowtriq",
  "event_type": "attack_start",
  "timestamp": "2025-03-10T14:22:00Z",
  "incident": {
    "id": 147,
    "title": "UDP Flood on web-prod-1",
    "severity": "critical",
    "attack_family": "udp_flood",
    "peak_pps": 2450000,
    "peak_pps_fmt": "2.45M",
    "peak_bps": 1547000000,
    "peak_bps_fmt": "1.4 Gbps",
    "source_ip_count": 8429,
    "duration_seconds": 0,
    "ai_summary": "A large 1.4 Gbps UDP flood from 8,429 source IPs targeting web-prod-1",
    "status": "active",
    "started_at": "2025-03-10T14:22:00Z",
    "resolved_at": null,
    "dashboard_url": "https://flowtriq.com/dashboard/incident?id=147"
  },
  "node": {
    "name": "web-prod-1",
    "ip_address": "203.0.113.10"
  }
}
```

Event Types
-----------

| Event          | Description                              |
|----------------|------------------------------------------|
| `attack_start` | New DDoS attack detected                 |
| `attack_update`| Ongoing attack metrics updated           |
| `attack_end`   | Attack resolved (auto-close in Alerta)   |
| `test`         | Test notification from Flowtriq dashboard|

References
----------

  * Flowtriq Webhook Docs: https://flowtriq.com/docs?section=webhooks
  * Flowtriq: https://flowtriq.com

License
-------

Copyright (c) 2025 Jacob Masse. Available under the MIT License.

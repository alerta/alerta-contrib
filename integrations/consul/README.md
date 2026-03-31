# Consul Integration

Forward [Consul](https://www.consul.io/) health-check alerts to [Alerta](https://alerta.io/), triggered by [consul-alerts](https://github.com/AcalephStorage/consul-alerts).

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

## Prerequisites

- [Consul](https://www.consul.io/) installed and running
- [consul-alerts](https://github.com/AcalephStorage/consul-alerts) installed and running

## Installation

Install the Python dependencies:

```bash
pip install python-consul alerta --upgrade
```

Then either clone the repo and install locally:

```bash
python setup.py install
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/consul
```

Make sure the `consul_alerta.py` script is accessible by consul-alerts and is executable.

## Configuration

### Environment Variables

| Variable      | Default     | Description         |
|---------------|-------------|---------------------|
| `CONSUL_HOST` | `127.0.0.1` | Consul agent host   |
| `CONSUL_PORT` | `8500`      | Consul agent port   |

### Consul KV Keys

Set these keys in the Consul KV store:

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `alerta/apiurl` | yes | — | Alerta API URL |
| `alerta/apikey` | yes | — | Alerta API key |
| `alerta/timeout` | no | `900` | Alert timeout in seconds |
| `alerta/max_retries` | no | `3` | Max API call attempts |
| `alerta/sleep` | no | `2` | Seconds between retry attempts |
| `alerta/origin` | no | `consul` | Alert origin |
| `alerta/alerttype` | no | `ConsulAlert` | Alert event type |
| `alerta/defaultenv` | no | `Production` | Default alert environment |
| `alerta/env/{hostname}` | no | — | Per-node environment override |

### consul-alerts Notifier

Register the custom notifier and notification profile:

```
consul-alerts/config/notifiers/custom/alerta  →  <path>/consul_alerta.py
consul-alerts/config/notif-profiles/default   →  { "Interval": 10 }
```

The notification profile keeps active alerts open in Alerta before the timeout removes them.

## Heartbeat

The `consul_heartbeat.py` script (installed as the `consul-heartbeat` command) sends a periodic heartbeat to the Alerta API. This lets Alerta know that the Consul integration is alive — if heartbeats stop arriving within the configured `timeout` window (default 900 seconds), Alerta will flag the integration as stale.

The heartbeat is **not** triggered by consul-alerts. You should run it on a cron job or systemd timer, for example every 5 minutes:

```bash
# crontab entry
*/5 * * * * consul-heartbeat
```

It reads its configuration (`alerta/apiurl`, `alerta/apikey`, `alerta/origin`, `alerta/timeout`, `alerta/max_retries`, `alerta/sleep`) from the same Consul KV keys listed above.

## References

- https://www.consul.io/
- https://github.com/hashicorp/consul
- https://github.com/AcalephStorage/consul-alerts

## License

Copyright (c) 2016 Marco Supino. Available under the MIT License.

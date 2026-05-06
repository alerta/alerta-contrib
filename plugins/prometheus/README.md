Prometheus Alertmanager Plugin
==============================

Two-way integration with Prometheus which will silence alerts in
Alertmanager when alerts are ack'ed in the Alerta console and delete
silences if those alerts are manually re-opened.

Uses the [Alertmanager API v2](https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml).
Requires Alertmanager >= 0.16.0 (v2 API). Alertmanager removed the
v1 API entirely in version 0.28.0.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/prometheus

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `prometheus` to the list of enabled `PLUGINS` in `alertad.conf`
server configuration file and set plugin-specific variables either in
the server configuration file or as environment variables.

```python
PLUGINS = ['prometheus']
```

**Settings**

| Setting | Default | Description |
|---------|---------|-------------|
| `ALERTMANAGER_API_URL` | `http://localhost:9093` | Alertmanager base URL |
| `ALERTMANAGER_SILENCE_DAYS` | `1` | Silence duration in days |
| `ALERTMANAGER_SILENCE_DURATION` | *none* | Silence duration with units (see below). Takes precedence over `ALERTMANAGER_SILENCE_DAYS`. |
| `ALERTMANAGER_SILENCE_FROM_ACK` | `False` | Create silences when alerts are ack'ed |
| `ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES` | `False` | Use Alertmanager's `externalUrl` for silence API calls |
| `ALERTMANAGER_SSL_VERIFY` | `True` | SSL verification. Set to `False` to disable, or a file path for a custom CA bundle. |
| `ALERTMANAGER_USERNAME` | *none* | Basic auth username |
| `ALERTMANAGER_PASSWORD` | *none* | Basic auth password |

All settings can be set as environment variables or in `alertad.conf`.

**Basic Example**

```python
PLUGINS = ['reject', 'prometheus']
ALERTMANAGER_API_URL = 'http://localhost:9093'
ALERTMANAGER_SILENCE_FROM_ACK = True
```

**Silence Duration**

By default, silences last 1 day. Use `ALERTMANAGER_SILENCE_DURATION` for
finer-grained control with time unit suffixes:

```python
ALERTMANAGER_SILENCE_DURATION = '2h'   # 2 hours
ALERTMANAGER_SILENCE_DURATION = '30m'  # 30 minutes
ALERTMANAGER_SILENCE_DURATION = '1w'   # 1 week
ALERTMANAGER_SILENCE_DURATION = '90s'  # 90 seconds
```

Supported units: `s` (seconds), `m` (minutes), `h` (hours), `d` (days), `w` (weeks).
Plain integers without a unit are treated as days for backward compatibility
with `ALERTMANAGER_SILENCE_DAYS`.

**Clustered Alertmanagers**

Prometheus docs specify that Prometheus should send all alerts to all
Alertmanagers. If you have configured `ALERTMANAGER_API_URL` to be a
load-balanced endpoint that mirrors requests, the following setting will
use Alertmanager's `externalUrl` for silence API calls instead:

```python
ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES = True
```

Alertmanager syncs silences across instances, so sending to a single
instance is sufficient. A load-balanced API that mirrors requests would
create duplicate silences.

SSL Verification
----------------

By default, SSL certificates are verified when connecting to Alertmanager.
To disable verification (e.g. for self-signed certificates) or to specify
a custom CA bundle:

```python
ALERTMANAGER_SSL_VERIFY = False               # disable SSL verification
ALERTMANAGER_SSL_VERIFY = '/path/to/ca.pem'   # use a custom CA bundle
```

Authentication
--------------

Prometheus Alertmanager [does not provide any form of authentication](https://prometheus.io/docs/operating/security/#authentication-authorization-and-encryption)
by default. For convenience, this plugin will support Basic Auth if it has
been configured (using a reverse proxy or otherwise). Any other form of
authentication will require development work by the user.

```python
ALERTMANAGER_USERNAME = 'promuser'
ALERTMANAGER_PASSWORD = 'prompass'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
alerta.plugins.prometheus: DEBUG - Alertmanager: Add silence for alertname=DiskFull instance=web01 timeout=86400
alerta.plugins.prometheus: DEBUG - Alertmanager: 200 - {"silenceID":"73373e3f-a928-450a-ba75-e9254297b483"}
alerta.plugins.prometheus: DEBUG - Alertmanager: Added silenceId 73373e3f-a928-450a-ba75-e9254297b483 to attributes
```

References
----------

  * Alertmanager API v2 OpenAPI Spec: https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml
  * Alertmanager Silences: https://prometheus.io/docs/alerting/alertmanager/#silences

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

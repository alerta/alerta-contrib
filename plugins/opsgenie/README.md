OpsGenie Plugin
================

Send OpsGenie messages for new alerts.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/opsgenie

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `opsgenie` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

SERVICE_KEY_MATCHERS takes an array of dictionary objects, mapping a regular
expression to a OpsGenie API integration key.  This allows sending alerts to
multiple OpsGenie service integrations, based on 'alert.resource'.

```python
PLUGINS = ['opsgenie']
OPSGENIE_SERVICE_KEY = ''  # default="not set"
SERVICE_KEY_MATCHERS = []  # default="not set"
```

The `DASHBOARD_URL` setting should be configured to link pushover messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

The `OPSGENIE_SEND_WARN` setting should be configured if you would like to send
informational and warning alerts onto OpsGenie.

```python
OPSGENIE_SEND_WARN = True   # default=False
```

The `OPSGENIE_SEVERITY_MAP` and `OPSGENIE_DEFAULT_SEVERITY` settings should be configured
to map Alerta severity to OpsGenie's priority.

```python
OPSGENIE_SEVERITY_MAP = { "critical": "P1", "warning": "P2", "informational": "P5" }  # this is also default
OPSGENIE_DEFAULT_SEVERITY = "P3"  # default="P3"
```

**Example**

```python
PLUGINS = ['reject', 'opsgenie']
OPSGENIE_SERVICE_KEY = '54A634B1-FB0C-4758-840F-5D808C89E70E'
SERVICE_KEY_MATCHERS = [ {"regex":"proxy[\\d+]","api_key":"6b982ii3l8p834566oo13zx9477p1zxd"} ]
DASHBOARD_URL = 'https://try.alerta.io'
OPSGENIE_SEND_WARN = False
```

References
----------

  * OpsGenie Integration API: https://www.opsgenie.com/docs/web-api/alert-api


WebHook
-------
At the time of writing, no webhook exists to accept changes from OpsGenie back to Alerta.  Doing
so may be possible using the standard Alerta API, correlating the originating Alerta id.  This
id is available as the `alias` field within the OpsGenie incident.


License
-------

Copyright (c) 2017 Kurt Westerfeld. Available under the MIT License.

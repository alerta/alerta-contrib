PagerDuty Plugin
================

Send PagerDuty messages for new alerts.

**Tip: Use this plugin in conjunciton with the PagerDuty webhook which will notify
Alerta when a PagerDuty notification has been acknowledged or closed.**

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/pagerduty

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `pagerduty` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['pagerduty']
PAGERDUTY_SERVICE_KEY = ''  # default="not set"
```

The `DASHBOARD_URL` setting should be configured to link pushover messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

**Example**

```python
PLUGINS = ['reject', 'pagerduty']
PAGERDUTY_SERVICE_KEY = '2a675ee0f6a640098ee05ac9378e4eba'
DASHBOARD_URL = 'https://try.alerta.io'
```

References
----------

  * PagerDuty Integration API: https://developer.pagerduty.com/documentation/integration/events/
  * Alerta PagerDuty Webhook: http://docs.alerta.io/en/latest/integrations.html#pagerduty

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

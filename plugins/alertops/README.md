AlertOps Plugin
================


Trigger Alerts in AlertOps.



For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/kamsrikanth/Integrations

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `alertops` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variable in the
server configuration file or the environment variables:

The `ALERTOPS_URL` variable is generated during integration configuration within the AlertOps console. This should be added to the server configuration file.

```python
PLUGINS = ['alertops']
ALERTOPS_URL = ''  # default="Not configured"
```
The `DASHBOARD_URL` setting should be configured in the server configuration file to link pushover messages to the Alerta console through the AlertOps webhook:

```python
DASHBOARD_URL = '' # default="Not Set"
```

**Example**

```python
PLUGINS = ['reject', 'alertops']
ALERTOPS_URL = 'https://notify.alertops/POSTAlert/c8490f30-1r492-ceks85-c833els8f10cd/Alerta'
DASHBOARD_URL = 'https://try.alerta.io'
```

References
----------

  * AlertOps Integration Docs:
 https://help.alertops.com/integrations/pre-built-integration-guides/alerta

License
-------

Copyright (c) 2019 AlertOps.

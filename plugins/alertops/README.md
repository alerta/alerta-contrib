AlertOps Plugin
================

Trigger Alerts in AlertOps.



For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

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

The `AO_URL` variable is generated during integration configuration within the AlertOps console. This should be added to the server configuration file.

```python
PLUGINS = ['alertops'] 
AO_URL = ''  # default="Not configured"
```
The `DASHBOARD_URL` setting should be configured in the server configuration file to link pushover messages to the Alerta console through the AlertOps webhook: 

```python
DASHBOARD_URL = '' # default="Not Set"
```

**Example**

```python
PLUGINS = ['reject', 'alertops']
AO_URL = 'https://notify.alertops/POSTAlert/c8490f30-1r492-ceks85-c833els8f10cd/Alerta'
DASHBOARD_URL = 'https://try.alerta.io'
```

References
----------

  * AlertOps Integration Docs: 
  https://help.alertops.com/en/collections/274084-integrations

License
-------

Copyright (c) 2019 AlertOps. 


Zabbix Plugin
=============

Two-way integration with Zabbix which will acknowledge events in
Zabbix when alerts are ack'ed or closed in the Alerta console.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/zabbix

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `zabbix` to the list of enabled `PLUGINS` in `alertad.conf`
server configuration file and set plugin-specific variables either in
the server configuration file or as environment variables.

```python
PLUGINS = ['zabbix']
```

The below settings are configured with reasonable defaults:

```python
ZABBIX_API_URL = 'http://localhost'
ZABBIX_USER = 'Admin'
ZABBIX_PASSWORD = 'zabbix'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
2016-11-20 23:02:40,623 - alerta.plugins[7394]: DEBUG - Server plug-in 'prometheus' found. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:50]
2016-11-20 23:02:40,623 - alerta.plugins[7394]: DEBUG - Server plug-in 'prometheus' not enabled in 'PLUGINS'. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:59]
```
```
...
```

References
----------

  * Zabbix API Reference: https://www.zabbix.com/documentation/3.2/manual/api/reference
  * JSON RPC Specification: http://www.jsonrpc.org/specification
  * PyZabbix: https://github.com/lukecyca/pyzabbix

License
-------

Copyright (c) 2017 Nick Satterly. Available under the MIT License.





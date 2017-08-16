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
DEBUG in __init__ [/usr/local/lib/python2.7/dist-packages/alerta/plugins/__init__.py:48]: Server plugin 'zabbix' installed.
INFO in __init__ [/usr/local/lib/python2.7/dist-packages/alerta/plugins/__init__.py:56]: Server plugin 'zabbix' enabled.
INFO in __init__ [/usr/local/lib/python2.7/dist-packages/alerta/plugins/__init__.py:59]: All server plugins enabled: reject, zabbix
```
```
DEBUG in alerta_zabbix [/usr/local/lib/python2.7/dist-packages/alerta_zabbix.py:49]: Zabbix: acknowledge (ack) event=test.alerta, resource=Zabbix server (eventId=39)
DEBUG in alerta_zabbix [/usr/local/lib/python2.7/dist-packages/alerta_zabbix.py:57]: Zabbix: event.acknowledge() => {u'eventids': [u'39']}
DEBUG in alerta_zabbix [/usr/local/lib/python2.7/dist-packages/alerta_zabbix.py:49]: Zabbix: acknowledge (closed) event=test.alerta, resource=Zabbix server (eventId=39)
DEBUG in alerta_zabbix [/usr/local/lib/python2.7/dist-packages/alerta_zabbix.py:66]: Zabbix: event.acknowledge() => {u'eventids': [u'39']}
```

References
----------

  * Zabbix API Reference: https://www.zabbix.com/documentation/3.2/manual/api/reference
  * JSON RPC Specification: http://www.jsonrpc.org/specification
  * PyZabbix: https://github.com/lukecyca/pyzabbix

License
-------

Copyright (c) 2017 Nick Satterly. Available under the MIT License.





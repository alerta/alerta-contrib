InfluxDB Plugin
===============

Send alerts to InfluxDB.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/pushover

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `pushover` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['pushover']
PUSHOVER_TOKEN = ''  # default="not set"
PUSHOVER_USER = ''  # default="not set"
```

The `DASHBOARD_URL` setting should be configured to link pushover messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

**Example**

```python
PLUGINS = ['reject','pushover']
PUSHOVER_TOKEN = 'KzGDORePKggMaC0QOYAMyEEuzJnyUi'
PUSHOVER_USER = 'e9e1495ec75826de5983cd1abc8031'
DASHBOARD_URL = 'http://try.alerta.io'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
2016-11-21 14:41:49,893 - alerta.plugins[62723]: DEBUG - Server plug-in 'pushover' found. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:50]
2016-11-21 14:41:49,894 - alerta.plugins[62723]: INFO - Server plug-in 'pushover' enabled. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:57]
```
```
2016-11-21 14:50:58,237 - alerta.plugins.pushover[68098]: DEBUG - Pushover.net: {'timestamp': 1479739858, 'expire': 900, 'user': 'uSi3YZGrQVLQaqamBxT2HWgYT3DPPX', 'message': u'Instance was terminated unexpectedly', 'url_title': 'View alert', 'sound': 'tugboat', 'retry': 299, 'title': u'Production: Critical alert for AWS - i-0000101 is InstanceTerminated', 'url': 'https://try.alerta.io/#/alert/2359f60d-4e78-4dfa-b1d8-cb07853ca10a', 'priority': 2, 'token': 'agLzCrzY77sztBwcfjrouWMLqTwPVj'} [in build/bdist.macosx-10.12-x86_64/egg/alerta_pushover.py:65]
2016-11-21 14:50:58,258 - requests.packages.urllib3.connectionpool[68098]: INFO - Starting new HTTPS connection (1): api.pushover.net [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/requests-2.11.1-py2.7.egg/requests/packages/urllib3/connectionpool.py:805]
2016-11-21 14:50:58,640 - requests.packages.urllib3.connectionpool[68098]: DEBUG - "POST /1/messages.json HTTP/1.1" 200 None [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/requests-2.11.1-py2.7.egg/requests/packages/urllib3/connectionpool.py:401]
2016-11-21 14:50:58,644 - alerta.plugins.pushover[68098]: DEBUG - Pushover.net: 200 - {"receipt":"rqq5a545r9ibtwjwpft218kjwovyzy","status":1,"request":"3e9bdc39a2c857e25625c83cc63cf959"} [in build/bdist.macosx-10.12-x86_64/egg/alerta_pushover.py:72]
```

References
----------

  * Pushover Message API: https://pushover.net/api

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

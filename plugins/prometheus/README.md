Prometheus Alertmanager Plugin
==============================

Two-way integration with Prometheus which will silence alerts in
Alertmanager when alerts are ack'ed in the Alerta console and delete
silences if those alerts are manually re-opened.

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

The below settings are configured with reasonable defaults:

```python
ALERTMANAGER_API_URL = 'http://localhost:9093'
ALERTMANAGER_SILENCE_DAYS = 1
```

Or, if you want to inherit silence timeout from ack timeout:

```python
ALERTMANAGER_API_URL = 'http://localhost:9093'
ALERTMANAGER_SILENCE_FROM_ACK = True
```


Prometheus docs specify that prometheus should send all alerts to all alertmanagers.  If you have configured your 
ALERTMANAGER_API_URL to be a load balanced endpoint that mirrors requests to a set of alertmanagers then the following setting 
will create/remove silences if alertmanager has set the externalUrl, the following will configure alerta to use that for silences
 instead of the Alertmanager API URL. 

Alertmanager syncs silences across all alertmanagers so only sendng it to one AM is appropriate. Using a load-balanced API that mirrors 
requests will create one unique silenceId per alertmanager instance and sync them across all alertmanagers, which is not necessary. 
```python
ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES = True
```

**Robust Perception Demo Example**

```python
PLUGINS = ['reject','prometheus']
ALERTMANAGER_API_URL = 'http://demo.robustperception.io:9093'  # default=http://localhost:9093
ALERTMANAGER_SILENCE_DAYS = 2  # default=1
```


Authentication
--------------

Prometheus Alertmanager [does not provide any form of authentication](https://prometheus.io/docs/operating/security/#authentication-authorization-and-encryption)
by default. For convenience, this plugin will support Basic Auth if it has
been configured (using a reverse proxy or otherwise). Any other form of
authentication will require development work by the user.

**Example of BasicAuth configuration**

```python
ALERTMANAGER_API_URL = 'http://localhost:9093'
ALERTMANAGER_USERNAME = 'promuser'
ALERTMANAGER_PASSWORD = 'prompass'
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
2016-11-21 10:42:55,572 - alerta.plugins.prometheus[8268]: DEBUG - Alertmanager: Add silence for alertname=DiskFull instance=web01 [in build/bdist.macosx-10.12-x86_64/egg/alerta_prometheus.py:35]
2016-11-21 10:42:55,582 - requests.packages.urllib3.connectionpool[8268]: INFO - Starting new HTTP connection (1): demo.robustperception.io [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/requests-2.11.1-py2.7.egg/requests/packages/urllib3/connectionpool.py:214]
2016-11-21 10:42:55,677 - requests.packages.urllib3.connectionpool[8268]: DEBUG - "POST /api/v1/silences HTTP/1.1" 200 44 [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/requests-2.11.1-py2.7.egg/requests/packages/urllib3/connectionpool.py:401]
2016-11-21 10:42:55,711 - alerta.plugins.prometheus[8268]: DEBUG - Alertmanager: 200 - {"status":"success","data":{"silenceId":29}} [in build/bdist.macosx-10.12-x86_64/egg/alerta_prometheus.py:59]
2016-11-21 10:42:55,715 - alerta.plugins.prometheus[8268]: DEBUG - Alertmanager: Added silenceId 29 to attributes [in build/bdist.macosx-10.12-x86_64/egg/alerta_prometheus.py:67]
```

References
----------

  * Alertmanager Silences: https://prometheus.io/docs/alerting/alertmanager/#silences
  * Robust Perception On-line Demo: http://demo.robustperception.io:9090/consoles/index.html

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

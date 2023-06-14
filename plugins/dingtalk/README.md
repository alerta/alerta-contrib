# AlertaPlugins
This repo contains the Dingtalk plugin for Alerta


DingTalk Plugin
================

Send new alerts to Dingtalk.


Installation
------------

Clone this GitHub repo and run:

    $ python setup.py install


Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `dingtalk` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

SERVICE_KEY_MATCHERS takes an array of dictionary objects, mapping a regular
expression to a Dingtalk webhook token.  This allows sending alerts to
multiple Dingtalk service integrations, based on 'alert.resource'.

```python
PLUGINS = ['dingtalk']
DING_WEBHOOK_URL = ''  # default="not set"
WEBHOOK_MATCHERS = []  # default="not set"
```

The `DASHBOARD_URL` setting should be configured to link pushover messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

**Example**

```python
PLUGINS = ['reject', 'dingtalk']
DING_WEBHOOK_URL = 'https://oapi.dingtalk.com/robot/send?access_token=fc89e66e'
WEBHOOK_MATCHERS = [ {"regex":"proxy[\\d+]", "webhook":"https://oapi.dingtalk.com/robot/send?access_token=f9216e240af"} ]
DASHBOARD_URL = 'https://try.alerta.io'
```

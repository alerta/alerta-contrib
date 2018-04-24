HipChat Plugin
==============

Send HipChat messages for new alerts.

If you have the Python Jinja2 package installed you can customize the
HipChat message format.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/hipchat

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `hipchat` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['hipchat']
HIPCHAT_ROOM = 'alerts'
HIPCHAT_API_KEY =  'W4Dll5plS0qrqXCpPwjwzF9pO2TJI2Oou9Xaq8je'
DASHBOARD_URL = 'http://try.alerta.io'
```

The `HIPCHAT_SUMMARY_FMT` configuration variable is a Jinja2 template
string and accepts any Jinja2 syntax. The formatter has access to two
variables in the template environment, 'alert' for all alert details
and 'config' for access to the alerta configuration.

If you have Jinja2 available you can try customizing the message like
this:

```python
HIPCHAT_SUMMARY_FMT = '<b>[{{ alert.status|capitalize }}]</b> [{{ alert.severity|upper }}] Event {{ alert.event }} on <b>{{ alert.resource }}</b> <a href="{{ config.DASHBOARD_URL }}/#/alert/{{ alert.id }}">{{ alert.id[:8] }}</a>'
```

References
----------

  * HipChat room notification API: https://www.hipchat.com/docs/apiv2/method/send_room_notification
  * Jinja2 templating language for Python: http://jinja.pocoo.org/docs/dev/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

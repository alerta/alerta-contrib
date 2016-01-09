HipChat Plugin
================

Send HipChat messages for new alerts.

If you have jinja2 installed you can customize the message sent.

Installation
------------

    $ python setup.py install


Configuration
-------------

```
HIPCHAT_ROOM = '123456'
HIPCHAT_API_KEY =  'xzxzxzxzxzxzxxzxzxzzx'
```

If you have jinja2 available you can try customizing the message like this:
```
HIPCHAT_ROOM = '123456'
HIPCHAT_API_KEY =  'xzxzxzxzxzxzxxzxzxzzx'
HIPCHAT_SUMMARY_FMT = '<b>[{{ alert.status|capitalize }}]</b> [{{ alert.severity|upper }}] Event {{ alert.event }} on <b>{{ alert.resource }}</b> <a href="{{ config.DASHBOARD_URL }}/#/alert/{{ alert.id }}">{{ alert.id[:8] }}</a>'
DASHBOARD_URL = 'http://try.alerta.io'
```

The HIPCHAT_SUMMARY_FMT is a jinja2 template string and accepts any jinja2 syntax. You have 2 variables in the environment, 'alert' for all alert details and 'config' for access to the alerta configuration.

References
----------

HipChat room notification API: https://www.hipchat.com/docs/apiv2/method/send_room_notification

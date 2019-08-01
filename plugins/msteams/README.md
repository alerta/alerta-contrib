Microsoft Teams Plugin
==============

Send Microsoft Teams messages for new alerts.

If you have the Python Jinja2 package installed you can customize the
Microsoft Teams message format.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/msteams

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `msteams` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['msteams']
MS_TEAMS_WEBHOOK_URL =  'https://outlook.office.com/webhook/.../IncomingWebhook/.../...'
DASHBOARD_URL = 'http://try.alerta.io'
```

The `MS_TEAMS_SUMMARY_FMT` configuration variable is a Jinja2 template
string or filename to a template file and accepts any Jinja2 syntax.
The formatter has access to two variables in the template environment,
'alert' for all alert details and 'config' for access to the alerta
configuration.

If you have Jinja2 available you can try customizing the message like
this:

```python
MS_TEAMS_SUMMARY_FMT = '<b>[{{ alert.status|capitalize }}]</b> [{{ alert.severity|upper }}] Event {{ alert.event }} on <b>{{ alert.resource }}</b><br>{{ alert.text }}'
```

The `MS_TEAMS_TEXT_FMT` configuration variable is a Jinja2 template
string or filename to a template file and accepts any Jinja2 syntax.
`MS_TEAMS_TEXT_FMT` formats `msTeamsMessage.text(alert.text)`, if omitted
no formatting is done on `alert.text`.

Teams Payload
-------------
With `MS_TEAMS_PAYLOAD` it's possible to fully customize the alert.
`MS_TEAMS_PAYLOAD` is Jinja2 template (string or filename) containing the full
HTTP POST [payload](https://docs.microsoft.com/en-us/outlook/actionable-messages/message-card-reference)(json) that's sent to `MS_TEAMS_WEBHOOK_URL`.

Example payload in [example-payload.json.j2](example-payload.json.j2) file.

References
----------

  * Pymsteams API: https://github.com/rveachkc/pymsteams
  * Jinja2 templating language for Python: http://jinja.pocoo.org/docs/dev/

License
-------

Copyright (c) 2017 Anton Delitsch. Available under the MIT License.

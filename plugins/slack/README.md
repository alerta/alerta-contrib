Slack Plugin
============

Send alerts to [Slack](https://slack.com/).

![Slack Message](./images/alerta-slack-plugin.png)

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/slack

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `slack` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['slack']
```

To configure the Slack plugin start by setting up an
[incoming webhook integration](https://my.slack.com/services/new/incoming-webhook/)
for your Slack channel and adding the following configuration settings to `alertad.conf`:

```
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
SLACK_ATTACHMENTS = True  # default=False
SLACK_CHANNEL = '' # if empty then uses channel from incoming webhook configuration

ICON_EMOJI = '' # default :rocket:
ALERTA_USERNAME = '' # default alerta

```

The `DASHBOARD_URL` setting should be configured to link Slack messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```


References
----------

  * Slack Incoming Webhooks: https://api.slack.com/incoming-webhooks

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

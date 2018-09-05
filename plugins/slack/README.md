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

```python
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
SLACK_ATTACHMENTS = True  # default=False
SLACK_CHANNEL = '' # if empty then uses channel from incoming webhook configuration
SLACK_CHANNEL_ENV_MAP = { 'Production' : '#alert-prod' } # Default=None (optionnal) Allow to specify a channel on a per-environment basis. SLACK_CHANNEL is used a default value

ICON_EMOJI = '' # default :rocket:
ALERTA_USERNAME = '' # default alerta

```

The `DASHBOARD_URL` setting should be configured to link Slack messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

The `SLACK_SUMMARY_FMT` configuration variable is a Jinja2 template
string and accepts any Jinja2 syntax. The formatter has access to two
variables in the template environment, 'alert' for all alert details
and 'config' for access to the alerta configuration.

If you have Jinja2 available you can try customizing the message like
this:

```python
SLACK_SUMMARY_FMT = '*[{{ alert.status|capitalize }}]* [{{ alert.severity|capitalize }}] Event {{ alert.event }} on *{{ alert.environment }} - {{ alert.resource }}*: {{alert.value}}\n{{alert.text}}\nAlert Console: <{{ config.DASHBOARD_URL }}|click here> / Alert: <{{ config.DASHBOARD_URL }}/#/alert/{{ alert.id }}|{{ alert.id[:8] }}>'
```

Slack Apps API
--------------
To use the Slack "Apps" API instead of an Incoming Webhook, create an application and 
obtain its OAuth token.  Use that to set ```SLACK_TOKEN``` and specify the 
URL endpoint to the new API entrypoint this way:

```python
SLACK_WEBHOOK_URL = 'https://slack.com/api/chat.postMessage'
SLACK_TOKEN = 'xoxp-903711738716-407999999999-433333333331-a844444444488888888822222222220c'
```

Ensure SLACK_CHANNEL is set for the default channel for alerts.  You may still use SLACK_CHANNEL_ENV_MAP.


References
----------

  * Slack Incoming Webhooks: https://api.slack.com/incoming-webhooks

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

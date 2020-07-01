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
SLACK_SKIP_FIRST = 5  # default=0, ability to skip first N dublicates
SLACK_CHANNEL = '' # if empty then uses channel from incoming webhook configuration
SLACK_CHANNEL_ENV_MAP = { 'Production' : '#alert-prod' } # Default=None (optional) Allow specifying a channel on a per-environment basis. SLACK_CHANNEL is used as a default value.
SLACK_CHANNEL_EVENT_MAP = { 'Node offline' : '#critical-alerts' } # Default=None (optional) Allow specifying a channel on a per-event basis. SLACK_CHANNEL is used as a default value.
SLACK_CHANNEL_SEVERITY_MAP = { 'critical' : '#critical-alerts', 'informational': '#noisy-feed' } # Default=None (optional) Allow specifying a channel on a per-severity basis. SLACK_CHANNEL is used as a default value.
SLACK_CHANNEL_MAP = { 'Production' : { 'critical' : '#prod-alerts' } } # Default=None (optional) Allow specifying a channel on both a per-environment and per-severity basis. SLACK_CHANNEL is used as a default value.

ICON_EMOJI = '' # default None
ALERTA_USERNAME = '' # default alerta

```

The `DASHBOARD_URL` setting should be configured to link Slack messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

The `SLACK_SUMMARY_FMT` configuration variable is a Jinja2 template string and
accepts any Jinja2 syntax. The formatter has access to the following variables
in the template environment:

| Variable        | Description                 |
| `alert`         | For all alert details       |
| `status`        | The updated alert status    |
| `config`        | alerta configuration        |
| `color`         | The computed severity color |
| `channel`       | The computed channel        |
| `emoji`         | The computed emojii         |

If you have Jinja2 available you can try customizing the message like
this:

```python
SLACK_SUMMARY_FMT = '*[{{ alert.status|capitalize }}]* [{{ alert.severity|capitalize }}] Event {{ alert.event }} on *{{ alert.environment }} - {{ alert.resource }}*: {{alert.value}}\n{{alert.text}}\nAlert Console: <{{ config.DASHBOARD_URL }}|click here> / Alert: <{{ config.DASHBOARD_URL }}/#/alert/{{ alert.id }}|{{ alert.id[:8] }}>'
```

Slack Payload
-------------

Sometimes the defaults chosen by the plugin won't be flexible enough.   In this case,
it is possible to use the full capability of the Slack post message API, documented
here: https://api.slack.com/methods/chat.postMessage.

To utilize the API, one must craft the HTTP POST payload, which is possible by utilizing
the Jinja2 template format mechanism, and supplying a `SLACK_PAYLOAD` configuration.
Each part of the template can be fully customized by template expansion.

You can utilize the full power of the Slack API with this approach, including adding
images, interactive buttons and menus.

Example:

```python
SLACK_PAYLOAD = {
  "channel": "{{ channel }}",
  "emoji": ":fire:",
  "text": "*[{{ alert.environment }}]* :: _{{ status }}_ :: _{{ alert.severity|capitalize }}_ :: _{{ alert.value }}_\n```{{ alert.text }}```",
  "attachments": [{
    "color": "{{ color }}",
    "fields": [
      {"title": "Resource", "value": "{{ alert.resource }}", "short": False },
      {"title": "Services", "value": "{{ alert.service|join(', ') }}", "short": False },
      {"title": "Event", "value": "{{ alert.event }}", "short": True },
      {"title": "Origin", "value": "{{ alert.origin }}", "short": True },
    ],
    "actions": [
      { "type": "button", "text": "Alert Console", "url": "{{ config.DASHBOARD_URL }}/#/alert/{{ alert.id }}" },
    ]
 }]
}
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
  * Slack post message API: https://api.slack.com/methods/chat.postMessage

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

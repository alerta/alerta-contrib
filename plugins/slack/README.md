Slack Plugin
============

Send alerts to [Slack](https://slack.com/).

![Slack Message](./images/alerta-slack-plugin.png)

Installation
------------

Run the following command on the Alerta server to install and register the new plugin:

    $ python setup.py install


Configuration
-------------

To configure the Slack plugin start by setting up an
[incoming webhook integration](https://my.slack.com/services/new/incoming-webhook/)
for your Slack channel and adding the following configuration settings to `alertad.conf`:

```
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
SLACK_ATTACHMENTS = True  # default=False
```

Lastly, add `slack` to the list of enabled plugins:

```
PLUGINS = ['reject', 'slack']
```

References
----------

Slack Incoming Webhooks: https://api.slack.com/incoming-webhooks

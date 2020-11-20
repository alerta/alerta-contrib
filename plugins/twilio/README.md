Twilio SMS Plugin
=================

Send SMS messages for new alerts using Twilio.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/twilio

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `twilio_sms` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['twilio_sms']
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = ''

TWILIO_TO_NUMBER = ''
TWILIO_FROM_NUMBER = ''
```

Multiple destination phone numbers can be configured in the `TWILIO_TO_NUMBER`
configuration setting if separated by a comma:

```python
TWILIO_TO_NUMBER = '+15555555,+4471234567'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

References
----------

  * Twilio Sending Messages: https://www.twilio.com/docs/api/rest/sending-messages

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

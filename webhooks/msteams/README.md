MS Teams Webhook
==============

Receive HttpPOST ack,close and blackout actions via webhook callbacks.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/msteams

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

The custom webhook will be auto-detected and added to the list of available API endpoints.

- Create apikey with _write:webhooks_ scope.
- Put apikey to `MS_TEAMS_APIKEY` config.
- Configure `MS_TEAMS_INBOUNDWEBHOOK_URL` to point to your alerta `/webhooks/msteams` url.
- Configure msteams [plugin](https://github.com/alerta/alerta-contrib/tree/master/plugins/msteams) `MS_TEAMS_PAYLOAD` to add potentialaction buttons to msteams
alerts. (Example in [example-payload.json.j2](../../plugins/msteams/example-payload.json.j2)

Example Request
--------------

```plain
curl -sSL -X POST -H 'Content-Type: application/json' \
  -H 'X-API-Key: <API_KEY>' \
  -d \
  '
    {
      "action": "ack",
      "alert_id": "32adb117-0045-4626-ad89-a258db98133f"
    }
  ' \
  'http://localhost:8080/api/webhooks/msteams'
```

References
----------

  * MS Teams message card reference: https://docs.microsoft.com/en-us/outlook/actionable-messages/message-card-reference#httppost-action

License
-------

Copyright (c) 2019 Jarno Huuskonen. Available under the MIT License.

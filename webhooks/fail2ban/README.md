Fail2Ban Webhook
================

Receive [Fail2Ban](https://www.fail2ban.org) ban notifications via webhook callbacks.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

```plain
python setup.py install
```

Or, to install remotely from GitHub run:

```plain
pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/fail2ban
```

**Note:** If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

### Alerta

The custom webhook will be auto-detected and added to the list of available API endpoints.

### Fail2Ban

See [Fail2Ban](../../integrations/fail2ban/README.md)

Example Request
--------------

```plain
curl -sSL -X POST -H 'Content-Type: application/json' -d \
  '
    {
      "hostname": "foo",
      "severity": "critical",
      "attributes": {
        "bannedIp": "1.2.3.4"
      },
      "environment": "Development",
      "resource": "SSHD",
      "event": "The IP 1.2.3.4 has just been banned by Fail2Ban after 6 attempts!",
      "message": "test"
    }
  ' \
  'http://localhost:8080/api/webhooks/fail2ban?api-key=<API_KEY>'
```

License
-------

Copyright (c) 2018 Milos Buncic. Available under the MIT License.

Matrix Plugin
===================

Send Matrix messages for new alerts.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/matrix

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `matrix` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['matrix']
MATRIX_HOMESERVER = ''    # default="not set"
MATRIX_ROOM = ''          # default="not set"
MATRIX_ACCESS_TOKEN = ''  # default="not set"
MATRIX_MESSAGE_TYPE = ''  # default="notice" | can be "notice" or "text"
```

The `DASHBOARD_URL` setting should be configured to link matrix messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

**Example**

```python
PLUGINS = ['reject','matrix']
MATRIX_HOMESERVER = 'https://matrix.org'
MATRIX_ROOM = '!VMKjBnKVghpiiBqwjEg:matrix.org'
MATRIX_ACCESS_TOKEN = '4yHuHptP2crTWvLdzUzvhPmoArz6mLTqN9DnpvY5mFDLEW8yxWEJLU8kg6nLUdDcxHS6SwXNrchKM2pmscgoAue2XxUfCrhWBtGtP7QtECTtQiE6h4HuSGu6Vj8F9Zdge'
MATRIX_MESSAGE_TYPE = 'notice'
DASHBOARD_URL = 'https://try.alerta.io'
```

References
----------

  * How to get an access token: https://www.matrix.org/docs/guides/client-server-api#login
  * Matrix message types: https://matrix.org/docs/spec/client_server/latest#m-room-message-msgtypes

License
-------

Copyright (c) 2021 Magnus Walbeck. Available under the MIT License.

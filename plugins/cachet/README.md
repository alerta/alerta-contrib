Cachet Plugin
=============

Send incidents to Cachet status page.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/cachet

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `cachet` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['cachet']
CACHET_API_URL = ''  # default="not set"
CACHET_API_TOKEN = ''  # default="not set"
CACHET_SSL_VERIFY = False
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

References
----------

  * Cachet status page docs: https://docs.cachethq.io/reference
  * Python Cachet Client: https://github.com/dmsimard/python-cachetclient

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

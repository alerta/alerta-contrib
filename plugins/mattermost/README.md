Mattermost Plugin
===============

Send alerts to Mattermost.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/mattermost

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `mattermost` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['mattermost']
MATTERMOST_URL = '' # default="not set"
MATTERMOST_TOKEN = '' # default="not set"
MATTERMOST_USERNAME = # '' default="alerta"
```

Create a new incoming webhook in your Mattermost installation.
See https://docs.mattermost.com/developer/webhooks-incoming.html

Templating
----------

No templating support at this time. Use hardcoded reasonable one.

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries with `mattermost` substring. Like:

```
--------------------------------------------------------------------------------
Server plugin 'mattermost' enabled. [in /venv/lib/python3.6/site-packages/alerta/utils/plugin.py:31]
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Server plugin 'mattermost' installed. [in /venv/lib/python3.6/site-packages/alerta/utils/plugin.py:23]
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
DEBUG - Starting new HTTPS connection (1): mattermost.example.com:443 [in /venv/lib/python3.6/site-packages/urllib3/connectionpool.py:823]
--------------------------------------------------------------------------------
```

References
----------

  * Mattermost: https://docs.mattermost.com/
  * Mattermost Icoming Webhooks: https://docs.mattermost.com/developer/webhooks-incoming.html
  * Matterhook: https://github.com/numberly/matterhook

License
-------

Copyright (c) 2018 Dmitrii Sitnikov, WWHW Ltd. Available under the MIT License.

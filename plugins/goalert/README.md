Goalert Plugin
================

Send goalert messages for new alerts.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/goalert

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `goalert` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

Add some configs to `alertad.conf`:
```
GOALERT_URL = 'https://alerta.example'
GOALERT_TOKEN = 'secret key'
GOALERT_VERIFY = '/usr/local/share/ca-certificates/ca.crt' # or False
```

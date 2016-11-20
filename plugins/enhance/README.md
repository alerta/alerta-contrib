Enhance Plugin (Example)
========================

This is an example plugin that demonstrates how to add attributes to alerts as they
are received by the Alerta API before being saved to the database.

Two alert attributes are added to all incoming alerts received by Alerta:

  * `isOutOfHours` - a boolean indicating whether the alert occured during or outside of business hours
  * `runBookUrl` - a dynamically generated link to a Run Book wiki based on the alert event name

This repo should be forked or copied and the python plugin modified to suit
the specific Alerta environment.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/enhance

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `enhance` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

If the "run book" attribute is used the `RUNBOOK_URL` should be changed
to a valid intranet URL.

**Example**

```python
PLUGINS = ['enhance', 'reject']
RUNBOOK_URL = 'http://www.example.com/wiki/RunBook'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
2016-11-20 19:46:15,492 - alerta.plugins[4297]: DEBUG - Server plug-in 'enhance' found. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:50]
2016-11-20 19:46:15,493 - alerta.plugins[4297]: INFO - Server plug-in 'enhance' enabled. [in /var/lib/.virtualenvs/alerta/lib/python2.7/site-packages/alerta_server-4.8.11-py2.7.egg/alerta/plugins/__init__.py:57]
```

References
----------

  * Run Books: https://en.wikipedia.org/wiki/Runbook

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

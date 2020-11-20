Normalise Plugin (Example)
==========================

This is an example plugin that demonstrates how plugins can be used
to "normalise" alerts from different monitoring sources to ensure
they conform to a standard before being saved to the database.

Normalise actions:

  * two alert attributes are checked for values and if no value is set they are assigned default values.
  * alert text is modified to prepend the severity level in capitals.

This repo should be forked or copied and the python plugin modified to suit
the specific Alerta environment.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/normalise

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `normalise` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

**Example**

```python
PLUGINS = ['reject','normalise']
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:


References
----------

  * Normalize Monitoring Traps: https://docops.ca.com/ca-service-operations-insight/3-2/en/administrating/event-management/event-management-example-scenarios/event-management-example-5-normalize-monitoring-traps

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

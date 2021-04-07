**IMPORTANT: Do not use. This plugin has been deprecated and is not
required for Alerta Releases 5.0 onwards. To set a global timeout
use the `ALERT_TIMEOUT` setting without installing this plugin.**

---

Customize Global Alert Timeout Plugin
=====================================

This plugin provides the capability to set the global alert timeout via
Alerta configuration or an environment variable named `ALERT_TIMEOUT`.

This plugin is useful in scenarios where the source of an alert (e.g.
Prometheus AlertManager) does not specifically include an explicit timeout
setting and the default global timeout value may not be too large.


Timeout actions:

  * The alert 'timeout' attribute is (re)set for each alert to the value specified


Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/timeout

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `timeout` to the list of enabled `PLUGINS` in the `alertad.conf` server
configuration file and set plugin-specific variables either in the server
configuration file or as environment variables.

**Example**

```python
PLUGINS = ['timeout']
ALERT_TIMEOUT = 2400

```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries referencing `Setting timeout for alert to 2400`

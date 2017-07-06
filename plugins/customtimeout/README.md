Customise Global Alert Timeout Plugin
==========================

This plugin provides the capabilijty to set the global alert timeout via ALerta configuration or an environment variable. 
This plugin is useful in scenarios where the source of an alert (e.g. Prometheus AlertManager) does not specifically include an explict timeout setting and the default global timeout value may not be too large. 


Customtimeout actions:

 
  * The alert 'timeout' attribute is (re)set for each alert to the value specified


Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install


Configuration
-------------

Add `customtimeout` to the list of enabled `PLUGINS` in the `alertad.conf` server configuration file and set plugin-specific variables either in the server configuration file or as environment variables.

**Example**

```python
PLUGINS = ['customtimeout']
CUSTOM_TIMEOUT = 2400

```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log entries referencing `Setting timeout for alert to 2400`


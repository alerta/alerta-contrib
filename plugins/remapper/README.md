Remapper Plugin
===============

This plugin will remap alert fields according to the mapping rules that you
define via plugin configuration.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/remapper

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `remapper` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['remapper']
```

Then configure the mapping rules as shown in the examples section below.

**Example**

```python
PLUGINS = ['enhance', 'remapper']
REMAPPER_MAPPING_RULES = "{ \"text\": \"service\", \"resource\": \"attributes.namespace\" }"
```

In the example above you can see the `REMAPPER_MAPPING_RULES` environment
variable which is used to defines a dictionary in JSON string format. Such
dictionary defines the following key-value pairs:

* "text": "service"
* "resource": "attributes.namespace"

Each "key" will be target alert field, and each "value" will be the source
alert field. The plugin will try to get the value of the source alert field
in order to store it in the source alert field.
So, in the example above, after the plugin has processed the alert, you
should see the following outcome:

* `alert.text` should store the value of `alert.service`
* `alert.resource` should store the value of `alert.attributes['namespace']`

Copyright (c) 2024 OJ. Available under the MIT License.

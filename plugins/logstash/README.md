Logstash Plugin
===============

Log alerts to Kibana using Logstash.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/logstash

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `logstash` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['logstash']
```

**Default Configuration**

```python
LOGSTASH_HOST = 'localhost'
LOGSTASH_PORT = 6379
```

**Example**

```python
PLUGINS = ['logstash', 'reject']
LOGSTASH_HOST = 'logger.example.com'
```

References
----------

  * Logstash: https://www.elastic.co/products/logstash
  * Kibana: https://www.elastic.co/products/kibana

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

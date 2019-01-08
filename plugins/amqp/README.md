AMQP Publisher Plugin
=====================

Publish alerts to an AMQP topic.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/amqp

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `amqp` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['amqp']
AMQP_URL = 'mongodb://localhost:27017/kombu'
AMQP_TOPIC = 'notify'
```

Note: By default the AMQP plugin is configured to use MongoDB as the
AMQP transport so it is not necessary to install RabbitMQ or some other
messaging backbone to make use of this plugin.

**RabbitMQ Example**

```python
PLUGINS = ['reject','amqp']
AMQP_URL = 'amqp://login:password@server:port//'  # => default RabbitMQ port=5672
AMQP_TOPIC = 'alerta.notify'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
--------------------------------------------------------------------------------
INFO in alerta_amqp [/opt/alerta/venv/lib/python2.7/site-packages/alerta_amqp-0.2.0-py2.7.egg/alerta_amqp.py:47]:
Sending message 07a5c93d-c5a5-4758-916c-ecec2c42181b to AMQP topic "alerta.notify"
--------------------------------------------------------------------------------
Sending message 07a5c93d-c5a5-4758-916c-ecec2c42181b to AMQP topic "alerta.notify"
```

References
----------

  * AMQP: https://www.amqp.org/
  * RabbitMQ: https://www.rabbitmq.com/tutorials/amqp-concepts.html
  * Kombu Transports: http://docs.celeryproject.org/projects/kombu/en/latest/userguide/connections.html#transport-comparison

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

PubSub Plugin
==============

Send alerts to pubsub.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

You need to install google cloud python package:

    $ sudo pip install --upgrade google-cloud

Follow this to configure [![authentication]](https://googlecloudplatform.github.io/google-cloud-python/stable/pubsub-usage.html#authentication-configuration)

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/pubsub

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `pubsub` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['pubsub']
```

License
-------

Copyright (c) 2016 Arindam Choudhury. Available under the MIT License.

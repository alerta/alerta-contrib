AWS SNS Plugin
==============

Send alerts to AWS SNS topic.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/sns

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `sns` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['sns']
AWS_ACCESS_KEY_ID = ''  # default="not set"
AWS_SECRET_ACCESS_KEY = ''  # default="not set"
```

**Default Configuration**

```python
AWS_REGION = 'eu-west-1"'  # default="eu-west-1"
AWS_SNS_TOPIC = 'notify'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

References
----------

  * Amazon Web Services SNS: https://aws.amazon.com/sns/getting-started/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

OP5 Plugin
=============

Send acknowledgments to OP5 monitor.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/op5

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `op5` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.
It is recommended to setup an local OP5 user if Active Directory login is enabled.
https://kb.op5.com/display/DOC/Default

```python
PLUGINS = ['op5']
OP5_API_URL = ''  # default="not set"
OP5_API_USERNAME = ''  # default="not set"
OP5_API_PASSWORD = ''
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

References
----------

  * OP5 monitor docs: https://kb.op5.com
  * Python OP5 Client: https://github.com/klarna/op5lib

License
-------

Copyright (c) 2017 Anton Delitsch. Available under the MIT License.
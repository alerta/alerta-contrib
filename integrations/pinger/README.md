Pinger Integration
==================

Monitor network availability using ICMP Ping and generate alerts on failures.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/pinger

Configuration
-------------

Add "ping targets" to `/etc/alerta/alert-pinger.targets`:

```yaml

```

References
----------



License
-------

Copyright (c) 2014-2016 Nick Satterly. Available under the MIT License.

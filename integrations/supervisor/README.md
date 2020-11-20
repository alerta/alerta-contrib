Supervisor Integration
======================

Trigger alerts and heartbeats based on process `supervisor` [events][1].

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/supervisor

Configuration
-------------

Copy the example configuration file `supervisord.conf.example` to `/etc`
and modify for your environment:

    $ sudo cp supervisord.conf.example /etc/supervisord.conf
    $ sudo vi /etc/supervisord.conf
    $ sudo supervisord


Troubleshooting
---------------

    $ sudo supervisord -c supervisord.conf.example -n

References
----------

  * supervisord Events: http://supervisord.org/events.html

License
-------

Copyright (c) 2015-2016 Nick Satterly. Available under the MIT License.

Supervisor
==========

Trigger alerts and heartbeats based on `supervisor` [events][1].

Installation
------------

Install supervisor and alerta python SDK:

    $ sudo pip install supervisor alerta

Configuration
-------------

Copy the example configuration file `supervisord.conf.example` to /etc and modify for your environment:

    $ sudo cp supervisord.conf.example /etc/supervisord.conf
    $ sudo vi /etc/supervisord.conf

Usage
-----

    $ sudo supervisord


Trouble Shooting
----------------

    $ sudo supervisord -c supervisord.conf.example -n


[1]: <http://supervisord.org/events.html> "Supervisor Events"
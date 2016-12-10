SNMP Trap Integration
=====================

SNMP trap listener sends alerts to Alerta.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Prerequisites
-------------

* Net-SNMP snmptrapd package - integration runs as a trap handler by Net-SNMP snmptrapd

To install `net-snmp` on RedHat/Centos Linux:

    $ yum -y install net-snmp net-snmp-utils

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/snmptrap

Configuration
-------------

Configure `snmptrapd` to execute `alerta-snmptrap` when an SNMP trap is
received:

    $ vi /etc/snmp/snmptrapd.conf

    authCommunity log,execute,net public
    format execute $a %a\n$A %A\n$s %s\n$b %b\n$B %B\n$x %#y-%#02m-%#02l\n$X %#02.2h:%#02.2j:%#02.2k\n$N %N\n$q %q\n$P %P\n$t %t\n$T %T\n$w %w\n$W %W\n%V~\%~%v\n
    traphandle default alerta-snmptrap

    $ vi /etc/sysconfig/snmptrapd

    export ALERTA_ENDPOINT="http://10.0.2.2:8080"

    $ service snmptrapd start

Troubleshooting
---------------

Stop `snmptrapd` and run it in the foreground:

    $ sudo service snmptrapd stop
    $ sudo ALERTA_ENDPOINT="http://10.0.2.2:8080" snmptrapd -Lsd -p /var/run/snmptrapd.pid -f

Tail syslog file:

    $ tail -f /var/log/messages

Send test trap:

    $ snmptrap -v2c -c public localhost "" .1.3.6.1.6.3.1.1.5.3.0 0 s "This is a test linkDown trap"

References
----------

  * Configuring SNMP Trapd: http://net-snmp.sourceforge.net/wiki/index.php/TUT:Configuring_snmptrapd

License
-------

Copyright (c) 2014-2016 Nick Satterly. Available under the MIT License.

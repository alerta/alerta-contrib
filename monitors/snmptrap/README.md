Alert on SNMP Traps
-------------------

Usage
-----

Runs as a trap handler by Net-SNMP snmptrapd.

Requires
--------

* Net-SNMP snmptrapd package.

Installation
------------

    $ git clone ...
    $ sudo python setup.py install

    $ yum -y install net-snmp net-snmp-utils

Configuration
-------------

    $ vi /etc/snmp/snmptrapd.conf

    authCommunity log,execute,net public
    format execute $a %a\n$A %A\n$s %s\n$b %b\n$B %B\n$x %#y-%#02m-%#02l\n$X %#02.2h:%#02.2j:%#02.2k\n$N %N\n$q %q\n$P %P\n$t %t\n$T %T\n$w %w\n$W %W\n%V~\%~%v\n
    traphandle default alerta-snmptrap

    $ vi /etc/sysconfig/snmptrapd

    export ALERTA_ENDPOINT="http://10.0.2.2:8080"

    $ service snmptrapd start


Trouble Shooting
----------------

1. Stop `snmptrapd` and run it in the foreground:

    $ sudo service snmptrapd stop
    $ sudo ALERTA_ENDPOINT="http://10.0.2.2:8080" snmptrapd -Lsd -p /var/run/snmptrapd.pid -f

2. Tail syslog file:

    $ tail -f /var/log/messages

3. Send test trap:

    $ snmptrap -v2c -c public localhost "" .1.3.6.1.6.3.1.1.5.3.0 0 s "This is a test linkDown trap"
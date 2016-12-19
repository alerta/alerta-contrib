SNMP Trap Integration
=====================

SNMP trap listener sends alerts to Alerta.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Prerequisites
-------------

* Net-SNMP snmptrapd package - integration runs as a trap handler by Net-SNMP snmptrapd

To install `net-snmp` on RedHat/Centos Linux:

    $ sudo yum -y install net-snmp net-snmp-utils

To install `net-snmp` on Ubuntu Xenial:

    $ sudo apt install -y snmptrapd snmp

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

Set Alerta API endpoint in the start-up script on `RedHat/Centos`:

    $ vi /etc/sysconfig/snmptrapd

    export ALERTA_ENDPOINT="http://localhost:8080"

Set Alerta API endpoint in the start-up script on Debian/Ubuntu:

    $ vi /etc/default/snmptrapd

    export ALERTA_ENDPOINT="http://localhost:8080"

Restart the `snmptrapd` service:

    $ sudo service snmptrapd restart

Transform Plugin
----------------

By default, SNMP traps are assigned reasonable values for each alert
attribute. However, to make SNMP traps useful sources of events it may
be necessary to do additional processing and assign relevant values
for `resource`, `event`, `severity` and others.

To achieve this in an extensible way, it is recommended to use a plugin
that transforms the original "trapvar" values stored as attributes in the
submitted SNMP trap alert to values like `severity` in the "pre-receive"
hook.

**Example Trapvars**

```json
  "alert": {
    "attributes": {
      "trapvars": {
        "_#": "3",
        "_1": "0:1:41:43.19",
        "_2": "iso.3.6.1.6.3.1.1.5.3.0",
        "_3": "\"This is a test linkDown trap\"",
        "_A": "0.0.0.0",
        "_B": "localhost",
        "_N": ".",
        "_O": "iso.3.6.1.6.3.1.1.5.3.0",
        "_P": "TRAP2, SNMP v2c, community public",
        "_T": "0",
        "_W": "Enterprise Specific",
        "_X": "15:05:45",
        "_a": "0.0.0.0",
        "_b": "UDP: [127.0.0.1]:48476->[127.0.0.1]:162",
        "_q": "0",
        "_s": "SNMPv2c",
        "_t": "1482073545",
        "_w": "6",
        "_x": "2016-12-18"
      }
    },
    ...
```

**Example Transform Plugin for Oracle EM Traps**

```python
class OracleTrapTransformer(PluginBase):

    def pre_receive(self, alert):

        alert.resource = alert.attributes['trapvars']['_3'].split('.',1)[0]

        if alert.attributes['trapvars']['_10'] in ['Serious', 'Critical']: # oraEM4AlertSeverity
            alert.severity = 'critical'
        elif alert.attributes['trapvars']['_10'] == 'Error'
            alert.severity = 'major'
        else:
            alert.severity = 'normal'

        alert.event = alert.attributes['trapvars']['_6'].replace(' ','')   # oraEM4AlertMetricName
        alert.value = alert.attributes['trapvars']['_14']                  # oraEM4AlertMetricValue
        alert.text = alert.attributes['trapvars']['_11']                   # oraEM4AlertMessage

        return alert

    def post_receive(self, alert):
        ...
```

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

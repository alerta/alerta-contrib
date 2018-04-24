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
    traphandle default /path/to/alerta-snmptrap

**NOTE**: Use the full path to the `alerta-snmptrap` script because
`snmpstrapd` only searches a few paths. Use `which alerta-snmptrap` to
get the full path for your installation.

Set Alerta API endpoint and load all MIBs in the start-up script on
`RedHat/Centos`:

    $ vi /etc/sysconfig/snmptrapd

    export MIBS=+ALL
    TRAPDRUN=yes
    export ALERTA_ENDPOINT="http://localhost:8080"

Set Alerta API endpoint and load all MIBs in the start-up script on
Debian/Ubuntu:

    $ vi /etc/default/snmptrapd

    export MIBS=+ALL
    TRAPDRUN=yes
    export ALERTA_ENDPOINT="http://localhost:8080"

Restart the `snmptrapd` service:

    $ sudo service snmptrapd restart

SNMP MIBs
---------

Download all base SNMP MIBs and any MIBs required for the specific
environment eg. Cisco, NetApp, Dell.

On Ubuntu, use `snmp-mibs-downloader` to download MIBs and install
them in the correct directory:

    $ apt-get install snmp-mibs-downloader

To test that the downloaded SNMP MIBs are used to translate any received
traps translate a "coldStart" trap with and without the "-m +ALL" option, like so:

    $ snmptranslate .1.3.6.1.6.3.1.1.5.1
    iso.3.6.1.6.3.1.1.5.1

    $ snmptranslate -m +ALL .1.3.6.1.6.3.1.1.5.1
    SNMPv2-MIB::coldStart

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

Snmptrap Format
---------------

| trapvar | Description                                                                                  |
----------|-----------------------------------------------------------------------------------------------
| $a      | the contents of the agent-addr field of the PDU (v1 TRAPs only)                              |
| $A      | the hostname corresponding to the contents of the agent-addr field of the PDU, if available, |
|         | otherwise the contents of the agent-addr field of the PDU (v1 TRAPs only).                   |
| $b      | PDU source address (Note: this is not necessarily an IPv4 address)                           |
| $B      | PDU source hostname if available, otherwise PDU source address (see note above)              | 
| $N      | enterprise string                                                                            | 
| $O      | oid as name or numbers                                                                       |
| $P      | security information from the PDU (community name for v1/v2c, user and context for v3)       |
| $q      | trap sub-type (numeric, in decimal)                                                          |
| $s      | SNMP Version                                                                                 |
| $t      | decimal number of seconds since the operating system epoch (as returned by time(2))          |
| $T      | the value of the sysUpTime.0 varbind in seconds                                              |
| $w      | trap number                                                                                  |
| $W      | trap description                                                                             |
| $x      | current date                                                                                 |
| $X      | current time                                                                                 |
| $\<n\>  | *nth* attribute                                                                              |
| $#      | number of varbinds                                                                           |

See http://net-snmp.sourceforge.net/docs/man/snmptrapd.html


Troubleshooting
---------------

Stop `snmptrapd` and run it in the foreground:

    $ sudo service snmptrapd stop
    $ sudo ALERTA_ENDPOINT="http://localhost:8080" snmptrapd -m +ALL -Lsd -p /var/run/snmptrapd.pid -f

Tail syslog file:

    $ tail -f /var/log/messages

Send test traps:

    $ sudo snmptrap -v2c -c public localhost "" .1.3.6.1.6.3.1.1.5.3.0 0 s "This is a test linkDown trap"
    $ sudo snmptrap -v2c -c public localhost "" .1.3.6.1.6.3.1.1.5.4.0 0 s "This is a test linkUp trap"

If the trap is not processed and nothing appears in the logs use `strace`
to generate system-level tracing of the daemon:

    $ ps -ef | grep snmp
    $ strace -ff -p <pid>

**Example strace Output**

```
[pid 23125] rt_sigaction(SIGTERM, NULL, {SIG_DFL, [], 0}, 8) = 0
[pid 23125] rt_sigaction(SIGTERM, {SIG_DFL, ~[RTMIN RT_1], SA_RESTORER, 0x7f3dc8225cb0}, NULL, 8) = 0
[pid 23125] stat("/sbin/alerta-snmptrap", 0x7fffc9511a70) = -1 ENOENT (No such file or directory)
[pid 23125] stat("/usr/sbin/alerta-snmptrap", 0x7fffc9511a70) = -1 ENOENT (No such file or directory)
[pid 23125] stat("/bin/alerta-snmptrap", 0x7fffc9511a70) = -1 ENOENT (No such file or directory)
[pid 23125] stat("/usr/bin/alerta-snmptrap", 0x7fffc9511a70) = -1 ENOENT (No such file or directory)
[pid 23125] write(2, "sh: 1: ", 7)      = 7
[pid 23125] write(2, "alerta-snmptrap: not found", 26) = 26
[pid 23125] write(2, "\n", 1)           = 1
[pid 23125] exit_group(127)             = ?
[pid 23125] +++ exited with 127 +++
```

From the above error it can be seen that is this example the `alerta-snmptrap`
script can't be found by `snmptrapd` which is why the trap isn't being processed.

References
----------

  * Configuring SNMP Trapd: http://net-snmp.sourceforge.net/wiki/index.php/TUT:Configuring_snmptrapd
  * Net SNMP command-line tool options: http://www.net-snmp.org/docs/man/snmpcmd.html

License
-------

Copyright (c) 2014-2017 Nick Satterly. Available under the MIT License.

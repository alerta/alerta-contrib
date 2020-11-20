Syslog Plugin
=============

Log alerts to syslog.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/syslog

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `syslog` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['syslog']
```

**Default Configuration**

```python
SYSLOG_FORMAT = '%(name)s[%(process)d]: %(levelname)s - %(message)s'
SYSLOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SYSLOG_FACILITY = 'local7'
```

**Example Configuration**

The defaults are enough for most use-cases or override them in the
`alertad.conf` configuration file:

```python
PLUGINS = ['reject','syslog']
SYSLOG_FACILITY = 'local0'
```

```
Nov 21 20:42:37 c9b52479 root[17771]: WARNING - {"origin": "alerta/c9b52479.local", "text": "Instance was terminated unexpectedly", "lastReceiveTime": "2016-11-21T20:42:37.449Z", "receiveTime": "2016-11-21T20:42:37.449Z", "trendIndication": "lessSevere", "rawData": "", "previousSeverity": "major", "event": "InstanceTerminated", "group": "Misc", "severity": "warning", "service": ["AWS"], "id": "2359f60d-4e78-4dfa-b1d8-cb07853ca10a", "environment": "Production", "type": "exceptionAlert", "status": "open", "repeat": false, "tags": [], "createTime": "2016-11-21T20:42:37.383Z", "lastReceiveId": "5fd153a4-6d4c-4d18-9774-5414b8ebe96c", "customer": null, "resource": "i-0000101", "duplicateCount": 0, "correlate": [], "value": "n/a", "timeout": 86400, "attributes": {"ip": "127.0.0.1"}, "history": []}
Nov 21 20:42:42 --- last message repeated 1 time ---
```

References
----------

  * BSD syslog Protocol: https://www.ietf.org/rfc/rfc3164.txt
  * Syslog Protocol RFC: https://tools.ietf.org/html/rfc5424

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

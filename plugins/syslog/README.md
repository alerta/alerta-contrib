alerta-logger
=============

Log alerts to syslog.

Installation
------------

    $ python setup.py install


Configuration
-------------

Add `syslog` to the list of enabled `PLUGINS`.

```
PLUGINS = ['reject', 'syslog']
```

The defaults are enough for most use-cases or override them in the `alertad.conf` configuration file:

```
SYSLOG_FORMAT = '%(name)s[%(process)d]: %(levelname)s - %(message)s'
SYSLOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SYSLOG_FACILITY = 'local7'
```

Example
-------

```
Aug  2 15:49:54 macbookpro alerta[47471]: ERROR - {"origin": "alerta/macbookpro.home", "text": "Host is down", "lastReceiveTime": "2016-08-02T14:49:54.353Z", "receiveTime": "2016-08-02T14:49:54.353Z", "trendIndication": "moreSevere", "rawData": "", "previousSeverity": "unknown", "event": "node_down", "group": "Network", "severity": "major", "service": ["Test"], "id": "66deab25-a02e-4233-84d7-0573a326447c", "environment": "Development", "type": "exceptionAlert", "status": "open", "repeat": false, "tags": [], "createTime": "2016-08-02T14:49:54.306Z", "lastReceiveId": "66deab25-a02e-4233-84d7-0573a326447c", "customer": null, "resource": "web04", "duplicateCount": 0, "correlate": [], "value": "n/a", "timeout": 86400, "attributes": {"ip": "127.0.0.1"}, "history": []}
```

License
-------

    Alerta monitoring system and console
    Copyright 2016 Nick Satterly

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
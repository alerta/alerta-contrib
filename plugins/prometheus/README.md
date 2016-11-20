Prometheus Alertmanager Plugin
==============================

Silence alerts in Alertmanager when acking alerts in the Alerta console
and delete silences if alerts are manually opened.

Installation
------------

    $ python setup.py install


Configuration
-------------

```
ALERTMANAGER_API_URL = 'https://prom.example.com:9093'  # default=http://localhost:9093
ALERTMANAGER_SILENCE_DAYS = n  # default=1
```

References
----------

https://prometheus.io/docs/alerting/alertmanager/#silences

Consul
==========

Trigger alerts based on [consul][1]. health checks, triggered by [consul-alerts][2]

Requirements:
==========

    consul
    consul-alerts
    python-consul
    alerta


Installation
------------
    $ pip install python-consul alerta --upgrade
    copy script to somewhere accessible by consul-alerts, make sure its executable

Configuration
-------------

    define these keys in consul KV store:

        consul-alerts/config/notifiers/custom/alerta:<path>/consul-alerta.py
        alerta/apikey:'api-key' // alerta key for api access (MUST)
        alerta/apiurl:'api-url' // alerta api url (MUST)
        alerta/timeout:900 // alarm timeout in alerta (default 900)
        alerta/max_retries:3 // max api call attemps (default 3)
        alerta/sleep:2 // sleep between attemps (default 2)
        alerta/origin:consul // alert origin (default consul)
        alerta/defaultenv:Production // default alert environment (MUST)
        alerta/env/{hostname}:Testing // exceptions for env of specific nodes (optional)
        alerta/alerttype:ConsulAlerts // alert type (default ConsulAlerts)
        consul-alerts/config/notif-profiles/default: { "Interval": 10 } // will keep active alerts "open" in alerta, before timeout removes them (must)


[1]: <https://github.com/hashicorp/consul> "Consul"
[2]: <https://github.com/AcalephStorage/consul-alerts> "Consul-Alerts"

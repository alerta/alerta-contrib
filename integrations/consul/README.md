Consul
==========

Trigger alerts based on [consul][1]. health checks, triggered by [consul-alerts][2]

Requirements:

    consul
    consul-alerts


Installation
------------

    copy script to somewhere accessible by consul-alerts, make sure its executable

Configuration
-------------

    define these keys in consul KV store:

        consul-alerts/config/notifiers/custom/alerta:<path>/consul-alerta.py
        alerta/apikey:'api-key' // alerta key for api access
        alerta/apiurl:'api-url' // alerta api url
        alerta/timeout:5 // item timeout in alerta (default 86400)
        alerta/max_retries:3 // max api attempts
        alerta/sleep:2 // sleep between attemps
        alerta/origin:consul // alert origin
        alerta/alerttype:ConsulAlerts // alert type

[1]: <https://github.com/hashicorp/consul> "Consul"
[2]: <https://github.com/AcalephStorage/consul-alerts> "Consul-Alerts"

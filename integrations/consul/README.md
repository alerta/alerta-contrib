Consul Integration
==================

Send alerts based on [consul](https://www.consul.io/). health checks,
triggered by [consul-alerts](https://github.com/AcalephStorage/consul-alerts)

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Prerequisites
-------------

Consul and [consul-alerts](https://github.com/AcalephStorage/consul-alerts)
is installed and running.

Installation
------------
    $ pip install python-consul alerta --upgrade
    copy script to somewhere accessible by consul-alerts, make sure its executable

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/consul


Configuration
-------------

Define these keys in consul KV store:

        consul-alerts/config/notifiers/custom/alerta:<path>/consul-alerta.py
        alerta/apikey:'api-key' // alerta key for api access (MUST)
        alerta/apiurl:'api-url' // alerta api url (MUST)
        alerta/timeout:900 // alarm timeout in alerta (default 900)
        alerta/max_retries:3 // max api call attemps (default 3)
        alerta/sleep:2 // sleep between attemps (default 2)
        alerta/origin:consul // alert origin (default consul)
        alerta/defaultenv:Production // default alert environment (optional - default Production)
        alerta/env/{hostname}:Testing // exceptions for env of specific nodes (optional)
        alerta/alerttype:ConsulAlerts // alert type (default ConsulAlerts)
        consul-alerts/config/notif-profiles/default: { "Interval": 10 } // will keep active alerts "open" in alerta, before timeout removes them (must)


References
----------

  * https://www.consul.io/
  * https://github.com/hashicorp/consul
  * https://github.com/AcalephStorage/consul-alerts

License
-------

Copyright (c) 2016 Marco Supino. Available under the MIT License.

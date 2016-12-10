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

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/consul


Configuration
-------------

Define these keys in consul KV store:

```
consul-alerts/config/notifiers/custom/alerta:<path>/consul-alerta.py
alerta/apikey:'api-key' // alerta key for api access
alerta/apiurl:'api-url' // alerta api url
alerta/timeout:900 // alarm timeout in alerta (default 86400)
alerta/max_retries:3 // max api call attemps
alerta/sleep:2 // sleep between attemps
alerta/origin:consul // alert origin
alerta/defaultenv:Production // default alert environment
alerta/env/{hostname}:Testing // exceptions for env of specific nodes
alerta/alerttype:ConsulAlerts // alert type
consul-alerts/config/notif-profiles/default: { "Interval": 10 } // will keep active alerts "open" in alerta, before timeout removes them
```

References
----------

  * https://www.consul.io/
  * https://github.com/hashicorp/consul
  * https://github.com/AcalephStorage/consul-alerts

License
-------

Copyright (c) 2016 Marco Supino. Available under the MIT License.

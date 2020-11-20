Pinger Integration
==================

Monitor network availability using ICMP Ping and generate alerts on failures.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/pinger

Configuration
-------------

Add "ping targets" to `alerta-pinger.targets` in the following format:

```yaml
---
- environment: Production
  service: [Web]
  targets:
    - search.twitter.com
    - www.nytimes.com
    - www.google.com
    - www.nyc.gov
    - newyork.yankees.mlb.com
```

References
----------

  * RFC792 Internet Control Message Protocol: https://tools.ietf.org/html/rfc792

License
-------

Copyright (c) 2014-2016 Nick Satterly. Available under the MIT License.

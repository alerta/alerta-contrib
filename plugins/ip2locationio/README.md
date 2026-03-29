IP2Locationio Plugin
====================

Query geolocation information for the origin IP address from IP2Location.io API.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Prerequisite
------------
This plugin requires an API key to function. You may sign up for a free API key at https://www.ip2location.io/pricing.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/ip2locationio

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `ip2locationio` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables. For example:

```python
PLUGINS = ['reject', 'remote_ip', 'geoip']
IP2LOCATIONIO_ACCESS_KEY = 'YOUR_IP2LOCATIONIO_API_KEY'
```

**Sample output**



```json
{
    "alert": {
        "attributes": {
            "as":"Google LLC"
            "asn":"15169",
            "city": "Mountain View",
            "country": "US",
            "ip": "8.8.8.8",
            "latitude":37.38605,
            "longitude":-122.08385,
            "state": "California",
            "time_zone":"-08:00",
            "zip_code":"94035"
        },
        ...
      }
    }
```
License
-------

Copyright (c) 2024 IP2Location.io. Available under the MIT License.
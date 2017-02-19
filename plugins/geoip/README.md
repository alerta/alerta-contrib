GeoIP Plugin
============

Use IP Geolocation to determine the physical location of the origin of alerts.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/geoip

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `geoip` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['geoip']
```

**freegeoip.net Example**

```python
PLUGINS = ['reject','geoip']
GEOIP_URL = 'http://freegeoip.net/json'  # default
```

```json
{
    "alert": {
        "attributes": {
            "geoip": {
                "city": "London",
                "country_code": "GB",
                "country_name": "United Kingdom",
                "ip": "86.128.7.160",
                "latitude": 51.5092,
                "longitude": -0.0955,
                "metro_code": 0,
                "region_code": "ENG",
                "region_name": "England",
                "time_zone": "Europe/London",
                "zip_code": "EC4N"
            },
            "ip": "86.128.7.160, 10.1.1.1"
        }
        ...
      }
    }
```

**ip-api.com Example**

```python
PLUGINS = ['reject','geoip']
GEOIP_URL = 'http://ip-api.com/json'
```

```json
{
    "alert": {
        "attributes": {
            "geoip": {
                "as": "AS2856 BTnet UK Regional network",
                "city": "East Dulwich",
                "country": "United Kingdom",
                "countryCode": "GB",
                "isp": "BT",
                "lat": 51.4521,
                "lon": -0.0615,
                "org": "BT",
                "query": "86.128.7.160",
                "region": "ENG",
                "regionName": "England",
                "status": "success",
                "timezone": "Europe/London",
                "zip": "SE22"
            },
            "ip": "86.128.7.160, 10.1.1.1"
        },
        ...
      }
    }
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
2016-11-20 21:54:48,627 - alerta.plugins.geoip[5416]: DEBUG - GeoIP lookup for IP: 86.128.7.160 [in build/bdist.macosx-10.12-x86_64/egg/alerta_geoip.py:19]
```

References
----------

  * IP Geolocation: https://en.wikipedia.org/wiki/Geolocation
  * freegeoip.net: http://freegeoip.net/
  * ip-api.com: http://ip-api.com/docs/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

InfluxDB Plugin
===============

Write alert values to InfluxDB as time-series data.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/influxdb

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `influxdb` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['influxdb']
```

**Default Configuration**

```python
INFLUXDB_DSN = 'influxdb://user:pass@localhost:8086/alerta'
INFLUXDB_MEASUREMENT = 'event'
```

**Examples**

Define a different DSN with valid username/password:

```python
INFLUXDB_DSN = 'influxdb://alerta:p8ssw0rd@localhost:8086/alerta'
```

Only override the database name:

```python
INFLUXDB_DATABASE = 'monitoring'
```

**Query Example**

Find diskUtil values for all "Web" services:

```SQL
$ influx -precision rfc3339
Connected to http://localhost:8086 version 1.2.2
InfluxDB shell version: 1.2.2
> use alerta
Using database alerta
> select * from event where service =~ /Frontend/;
name: event
time                     environment event    resource    service      severity value
----                     ----------- -----    --------    -------      -------- -----
2017-05-19T21:13:41.494Z Production  diskUtil host01:/tmp Web,Frontend major    98.01
2017-05-19T21:14:31.92Z  Production  diskUtil host02:/var Web,Frontend minor    79.54
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

References
----------

  * InfluxDB: https://docs.influxdata.com/influxdb/latest/

License
-------

Copyright (c) 2016-2017 Nick Satterly and [AUTHORS](/AUTHORS). Available under the MIT License.

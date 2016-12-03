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
$ influx
Visit https://enterprise.influxdata.com to register for updates, InfluxDB server management, and monitoring.
Connected to http://localhost:8086 version v1.1.0
InfluxDB shell version: v1.1.0
> use alerta
Using database alerta
> select * from diskUtil where service =~ /Web/
name: diskUtil
time                        customer      environment   resource       service        value
----                        --------      -----------   --------       -------        -----
2016-12-04T15:56:05.116Z    ACME Corp.    Production    host01:/tmp    Web,Frontend   87.8
2016-12-04T16:11:44.032Z    ACME Corp.    Production    host02:/tmp    Web,API        66.1
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

References
----------

  * InfluxDB: https://docs.influxdata.com/influxdb/latest/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.

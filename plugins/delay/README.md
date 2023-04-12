# Delay filter plugin

[Shelve](https://docs.alerta.io/en/latest/cli.html#shelve-shelve-alerts) alerts to prevent notifications within a set timout.  
The delay plugin uses [Alerta Filter](https://docs.alerta.io/en/latest/server.html#filters).

A received alert that matches any filters will be shelved. The matching is the same as for [Blackout Periods](https://docs.alerta.io/en/latest/server.html#blackout-periods).  
The alert will remain shelved for the duration of the timeout set in filter, config or in the plugin it self.  
If the alert hasn't cleared within the timout, [housekeeper](https://docs.alerta.io/en/latest/cli.html#housekeeping-expired-and-clears-old-alerts) will pick up the alert and unshelve it.


## Installation

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/delay

Note: If Alerta is installed in a python virtual environment then plugins need to be installed into the same environment for Alerta to dynamically discover them.


## Configuration

`DELAY_TIMEOUT` - Integer. The default timeout for delay filters. Plugin defaults to `120` if not set.  
`DELAY_MATH` -  String.  'max' or 'min'. What timeout to choose. `'max'` will take the highest timeout of the matching filters. Plugin defaults to the first match if not set.   
`DELAY_AUTOUNSHELVE` - Boolean. By default an re-opened alert will enter it's last status. If the configuration is set to `True`, alerts will be auto-unshelved when re-opened. This is for alerts where filters does not match. Plugin defaults to `False` if not set.

```python
PLUGINS = ['delay']
DELAY_TIMEOUT = 120 
DELAY_MATH = 'max'
DELAY_AUTOUNSHELVE = True
```


## Parameters

Parameters to pass to filters are:  
`type: "delay"` - To create a filter with the delay plugin.  
`attributes: {"timeout": NNN}` - Timeout in seconds (integer). How long the alert is to be shelved.

See [Alerta API - Filters](https://docs.alerta.io/en/latest/api/reference.html#filters) for all inputs.


### Examples

```
curl -XPOST http://localhost:8080/filter \
-H 'Authorization: Key demo-key' \
-H 'Content-type: application/json' \
-d '{
      "environment": "Production",
      "service": ["example.com"],
      "type": "delay",
      "attributes": {
        "timeout": 300
      }
    }'
```


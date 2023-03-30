# JSON validation explanation

## Description

We  use a json schema valation made in python via the plugin architecture of alerta to execute this.

## working

The plugin must be installed into the python packages that are used by alerta.
At startup alerta will  read the required plugins from confg try to locate the plugins and load them.

Every incoming request will then be validated against the pre_recieve method in the plugin.
this method will read the json recieved and validate it againt the schema present on disk of the alarta server.
That file is located by opening the file that is specified in the alerta config as JSON_SCHEMA.

Successful validations will proceed to alerta, failed validations will be rejected with an HTTP 422 error: unprocessable entity

## installation and  configuration

- Install the plugin python3 setup.py install
- Add the plugin to the alerta configuration file
   PLUGINS=['json_schema']
- add a line with path to json schema:
   JSON_SCHEMA = '/opt/alerta/schema.json'
- put json schema at that path
- restart alerta

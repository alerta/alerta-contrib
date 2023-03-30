# json_schema
validates alert to a provided jsonschema
Use the alerta plugin pre_recieve hook to run code before alerta accepts alarm for caller.
If the validation fails caller recieves an HTTP error code, and the alarm is not saved.

## build test
Setup with setupptools
increment version number in setup.py
python3 setup.py install will install the module
restart alerta for the module to get loaded into alerta.
Check the logs for any load module errors or errors during alarm submit


## install
refer to the doc directory
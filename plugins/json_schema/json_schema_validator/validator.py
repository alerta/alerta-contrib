import jsonschema
import json
import logging
LOG = logging.getLogger('alerta')
def validate(schema,jsonfile):
    LOG.debug("schema is " + schema)
    with open(schema, 'r') as schema_file:
        loadedschema = json.loads(schema_file.read())
    jsonschema.validate(jsonfile,loadedschema)



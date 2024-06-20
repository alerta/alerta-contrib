import logging
import os
from sqlite3 import InternalError
from xml.dom import NotFoundErr
from alerta.utils.api import process_action
from alerta.app import alarm_model
from alerta.exceptions import AlertaException
from alerta.plugins import PluginBase
from json_schema_validator import validator
from jsonschema import *
import pprint
import json
import jsonschema

LOG = logging.getLogger('alerta')
SCHEMA_VAR = "JSON_SCHEMA"

import pprint
try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
    
    
TIMEOUT = os.environ.get('ALERT_TIMEOUT') or app.config.get('ALERT_TIMEOUT', '0')


        
        
def alert_json(alert):
    """
    copy all the relevant properties from the incoming alert for processing by json-schema
    """
    tocopy = ["timeout","resource","event", "environment", "severity",  "correlate", "status", "service", "group", "value", "text", "tags","attributes", "event_type","raw_data","customer"]
    alarmobj = {}
    for item in tocopy: #remove all empty values to avoid validating non present elements as empty
        LOG.debug(item)
        if hasattr(alert,item):
            if (getattr(alert,item) != None):
                alarmobj[item]= getattr(alert,item)
        else:
            LOG.debug("skip " + item  +" hasattr is false")
    LOG.debug(pprint.pformat(alarmobj))
    return alarmobj

class AlertaJsonSchema(PluginBase):
    """
    Validate the incoming alert against a JSON schema file specified in config

    """
    def pre_receive(self, alert, **kwargs):
        LOG.debug("Json schema plugin: start validation")
        jsonfile = app.config.get(SCHEMA_VAR , '0')
        if ( jsonfile == '0'):
            raise AlertaException("could not fine "+SCHEMA_VAR+" in alerta config file")
        try:
            validator.validate(jsonfile,alert_json(alert))  
        except  jsonschema.exceptions.ValidationError as e: #unprocessable entity
            raise AlertaException(message=e.message + "on " + e.absolute_path  + " refer to the json schema", code=422)
        return alert


    def post_receive(self, alert, **kwargs):
        return

    def status_change(self, alert, status, text, **kwargs):
        return
    def take_action(self, alert, action, text, **kwargs):
        return

    def take_note(self, alert, text, **kwargs):
        raise NotImplementedError

    def delete(self, alert, **kwargs) -> bool:
        raise NotImplementedError


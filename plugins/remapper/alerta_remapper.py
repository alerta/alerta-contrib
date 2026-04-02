import logging
import os
import json

from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.remapper')

# Try loading the mapping rules via environment variables first
try:
    # The environment variable must be a string formatted as follows:
    #   REMAPPER_MAPPING_RULES="{ \"text\": \"service\", \"resource\": \"attributes.namespace\" }"
    LOG.debug('Trying to load remapper config in JSON format')
    REMAPPER_MAPPING_RULES = json.loads(os.environ.get('REMAPPER_MAPPING_RULES'))
except Exception:
    # Otherwise, we'll try grabbing the mapping rules from the application config
    # which must be passed in dictionary format, for instance:
    #   REMAPPER_MAPPING_RULES = {
    #       "text": "service",
    #       "resource": "attributes.namespace"
    #   }
    LOG.debug('Attempting to load remapper config via app config')
    REMAPPER_MAPPING_RULES = app.config.get('REMAPPER_MAPPING_RULES', dict())


class RemapAlert(PluginBase):

    def pre_receive(self, alert):
        LOG.debug('(pre_receive) Remapping alert fields...')

        # Go through each mapping rule
        for target, source in REMAPPER_MAPPING_RULES.items():
            # Check if we're dealing with a nested dictionary property (only one level deep is supported)
            if '.' in source:
                dict_name, dict_key = source.split('.', 1)
                if hasattr(alert, dict_name):
                    nested_dict = getattr(alert, dict_name)
                    if isinstance(nested_dict, dict) and dict_key in nested_dict:
                        setattr(alert, target, nested_dict[dict_key])
            else:
                # Regular attribute remapping
                if hasattr(alert, source):
                    setattr(alert, target, getattr(alert, source))

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return

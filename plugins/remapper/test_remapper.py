import unittest
from unittest.mock import patch
import os

from alerta.models.alert import Alert
from alerta_remapper import RemapAlert

class RemapperPluginTestCase(unittest.TestCase):

    def setUp(self):
        self.alert = Alert(
            resource='My Resource',
            event='My Event',
            environment='Development',
            customer='My Customer',
            severity='critical',
            service='My Service',
            group='My Group',
            value='My Value',
            text='My Text',
            attributes={
                'namespace': 'My Client'
            },
            timeout=3600
        )

    # This test case relies on the default mapping rules, so it expects no mapping to take place.
    def test_empty_rules(self):
        remapper = RemapAlert()
        result = remapper.pre_receive(self.alert)
        self.assertEqual(result.resource, self.alert.resource)
        self.assertEqual(result.event, self.alert.event)
        self.assertEqual(result.environment, self.alert.environment)

    # IMPORTANT: we are actually patching the module variable, which skips the actual init logic
    # that it's done for it. As a result, this approach works for testing the method that relies
    # on said module variable, but fails to test the init logic associated to it.
    @patch('alerta_remapper.REMAPPER_MAPPING_RULES', new={ "text": "customer", "service": "group" })
    def test_simple_properties_mapping(self):
        remapper = RemapAlert()
        result = remapper.pre_receive(self.alert)
        self.assertEqual(result.text, self.alert.customer)
        self.assertEqual(result.service, self.alert.group)

    # IMPORTANT: same comment as in the test case above.
    @patch('alerta_remapper.REMAPPER_MAPPING_RULES', new={ "resource": "attributes.namespace" })
    def test_nested_properties_mapping(self):
        remapper = RemapAlert()
        result = remapper.pre_receive(self.alert)
        self.assertEqual(result.resource, self.alert.attributes['namespace'])

if __name__ == "__main__":
    unittest.main()

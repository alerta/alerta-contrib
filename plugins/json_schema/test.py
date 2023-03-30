import unittest
import json_schema_validator.validator as validator
import os
import json
import jsonschema.exceptions
TEST_DIR = "test" + os.sep
SCHEMA = "schema.json"




class ValidatorTest(unittest.TestCase):
        def testValidJsonFile(self):
            test = json.load(open(TEST_DIR + "valid.json"))
            validator.validate(SCHEMA,test)

        def testMissingResource(self):
            """Test if invalid json fails"""
            test = json.load(open(TEST_DIR + "missing.json"));
            try:
                validator.validate(SCHEMA,test)
            except jsonschema.exceptions.ValidationError:
                assert True
            else:
                assert False          
if __name__ == "__main__":
    unittest.main() # run all tests
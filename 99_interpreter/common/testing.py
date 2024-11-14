import unittest, os, json
from abc import ABC

# THE ENVIRONMENT VAR THAT UNITTESTS REQUIRE TO OBTAIN DYNAMIC ARGUMENTS
env_var_name: str = '_UNITTEST_ARGS'

################################################################################################
################################################################################################

# SHARED CONSTRUCTOR FOR ALL UNITTESTS
class unittest_base(unittest.TestCase, ABC):
    def setUp(self):
        stringified_dict: str = os.environ.get(env_var_name)
        self.input_params: dict = json.loads(stringified_dict)

    # COMPARE TWO DICTS FOR SCHEMATIC DIFFERENCES
    def validate_schema(self, user_dict: dict, ref_dict: dict, root_path=''):
        for key in ref_dict.keys():

            # CONSTRUCT KEY PATH FOR DEBUGGING CLARITY
            path: str = f'{root_path}.{key}'
            if len(root_path) == 0: path = key

            # MAKE SURE THE KEY EXISTS
            key_error: str = f"KEY '{path}' NOT FOUND"
            self.assertTrue(key in user_dict, msg=key_error)

            # KEEP UNRAVELING DICTS
            if isinstance(ref_dict[key], dict):
                self.validate_schema(user_dict[key], ref_dict[key], path)

            # OTHERWISE, VERIFY THAT VALUE TYPE IS CORRECT
            else:
                value_type = type(user_dict[key])
                expected_type = ref_dict[key]

                value_error: str = f"KEY '{path}' IS OF WRONG TYPE (EXPECTED {value_type}, GOT {expected_type})"
                self.assertTrue(value_type == expected_type, msg=value_error)

################################################################################################
################################################################################################

# WRAPPER TO PROGRAMMATICALLY INVOKE THE UNITTESTS OF A SPECIFIC MODULE
def run_tests(module_dir: str, input_data: dict):
    assert isinstance(module_dir, str), f"ARG 'module_dir' MUST BE OF TYPE STR (GOT {type(module_dir)})"
    assert isinstance(input_data, dict|list), f"ARG 'input_args' MUST BE OF TYPE DICT (GOT {type(input_data)})"

    # MAKE INPUT ARGS AVAILABLE FOR THE UNITTESTS THROUGH ENVIRONMENT
    os.environ[env_var_name] = json.dumps(input_data)

    # LOAD THE TESTSUITE
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=module_dir, pattern=f'*tests.py')

    # RUN THE TESTS    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
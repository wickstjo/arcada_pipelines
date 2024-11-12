import unittest, os, json
from abc import ABC

# THE ENVIRONMENT VAR THAT UNITTESTS REQUIRE TO OBTAIN DYNAMIC ARGUMENTS
env_var_name: str = '_UNITTEST_ARGS'

# SHARED CONSTRUCTOR FOR ALL UNITTESTS
class unittest_base(unittest.TestCase, ABC):
    def setUp(self):
        stringified_dict: str = os.environ.get(env_var_name)
        self.input_args: dict = json.loads(stringified_dict)

# WRAPPER TO PROGRAMMATICALLY INVOKE THE UNITTESTS OF A SPECIFIC MODULE
def run_tests(module_name: str, input_args: dict):
    assert isinstance(module_name, str), f"ARG 'module_name' MUST BE OF TYPE STR (GOT {type(module_name)})"
    assert isinstance(input_args, dict), f"ARG 'input_args' MUST BE OF TYPE DICT (GOT {type(input_args)})"

    # MAKE INPUT ARGS AVAILABLE FOR THE UNITTESTS THROUGH ENVIRONMENT
    os.environ[env_var_name] = json.dumps(input_args)

    # LOAD THE TESTSUITE
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='actions', pattern=f'{module_name}.py')

    # RUN THE TESTS    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
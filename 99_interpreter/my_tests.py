import unittest, os, json

class my_unit_tests(unittest.TestCase):

    # READ DYNAMIC ARGS FROM INTERPRETER
    def setUp(self):
        env_var_name: str = 'UNITTEST_ARGS'
        stringified_dict: str = os.environ.get(env_var_name)
        self.input_args: dict = json.loads(stringified_dict)

    def test_first(self):
        print(self.input_args)
        self.assertEqual(True, True)

foo = my_unit_tests()
foo.run()
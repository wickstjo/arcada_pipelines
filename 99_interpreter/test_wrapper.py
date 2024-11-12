import unittest

def run_tests():
    # Specify the path to the test file or module
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='.', pattern='my_tests.py')
    
    # Create a test runner that will output the results
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)

run_tests()
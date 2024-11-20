from common.testing import unittest_base
import random, time

class validation_tests(unittest_base):
    def test_feature_shift_column_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'target_column': str,
            'shift_by': int,
            'output_column': str
        }, root_path='shift_column.feature_params')
from common.testing import unittest_base
import random, time

class validation_tests(unittest_base):
    def test_feature_vectorize_df_00_validate_input(self):

        # MAKE SURE INPUT PARAMS MATCH REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'feature_columns': list,
        }, root_path='vectorize_df.feature_params')
from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class stochastic_k(base_feature):
    def __init__(self, input_params: dict):
        self.window_size = input_params['window_size']
        self.output_column = input_params['output_column']

    # CREATE THE FEATURE VECTOR THROUGH SEPARATE
    # FUNCTION TO MAKE IT EASIER TO UNITTEST
    def transform(self, dataframe: DataFrame):
        dataframe[self.output_column] = self.create_feature_vector(dataframe)
        return dataframe
    
        # UNITTEST TODO: REQUIRED COLUMNS EXIST
        # UNITTEST TODO: COMPARE AGAINST EXPECTED VECTOR VALUES -- INCLUDE NANS
        # UNITTEST TODO: CHECK THAT VECTOR IS SAME LENGTH AS DF -- NO DROP NANS
    
    def create_feature_vector(self, dataframe: DataFrame):
        p1 = dataframe['close'] - dataframe['low'].rolling(self.window_size).min()
        p2 = dataframe['high'].rolling(self.window_size).max() - dataframe['low'].rolling(self.window_size).min()
        series = 100 * (p1 / p2)

        return list(series)
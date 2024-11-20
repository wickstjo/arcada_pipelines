from actions.feature_engineering.base_feature import base_feature
from pandas import DataFrame

class vectorize_df(base_feature):
    def __init__(self, input_params: dict):
        self.feature_columns = input_params['feature_columns']
    
    def transform(self, dataframe: DataFrame):
        df_columns = list(dataframe.columns)

        for column_name in self.feature_columns:
            assert column_name in df_columns, f"COLUMN '{column_name}' MISSING FROM DATASET"

        # EXTRACT JUST THE VALUES OF THE FEATURE COLUMNS
        return dataframe[self.feature_columns].values.tolist()
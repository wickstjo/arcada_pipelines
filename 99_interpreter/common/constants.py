from assertpy import assert_that

class repository:
    def __init__(self, options_mapping):
        self.options = options_mapping
        self.keys = list(options_mapping.keys())
    
    # FETCH OPTION
    def get(self, option_name: str):
        assert_that(option_name).is_type_of(str)
        assert_that(self.options).contains_key(option_name)

        return self.options[option_name]
    
    # FETCH & INSTANTIATE OPTION
    def create(self, option_name: str, option_params: dict = {}):
        assert_that(option_params).is_type_of(dict)

        # WITH PARAMS
        if len(option_params) > 0:
            return self.get(option_name)(option_params)

        # WITHOUT PARAMS
        return self.get(option_name)()

#####################################################################################
### AVAILABLE FEATURES

from actions.features.shift_column.shift_column import shift_column
from actions.features.stochastic_k.stochastic_k import stochastic_k
from actions.features.to_dataframe.to_dataframe import to_dataframe
from actions.features.drop_nan_rows.drop_nan_rows import drop_nan_rows
from actions.features.to_feature_matrix.to_feature_matrix import to_feature_matrix

feature_repo = repository({

    # NORMAL YAML FEATURES
    'shift_column': shift_column,
    'stochastic_k': stochastic_k,

    # "HIDDEN" FEATURES
    'drop_nan_rows': drop_nan_rows,
    'to_dataframe': to_dataframe,
    'to_feature_matrix': to_feature_matrix,
})

#####################################################################################
### AVAILABLE SCALERS

from sklearn.preprocessing import StandardScaler, MinMaxScaler

scaler_repo = repository({
    'standard_scaler': StandardScaler,
    'minmax_scaler': MinMaxScaler,
})

#####################################################################################
### AVAILABLE MODELS

from sklearn.linear_model import LinearRegression

model_repo = repository({
    'linear_regression': LinearRegression,
})
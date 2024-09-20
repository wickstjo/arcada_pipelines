from machine_learning.model_suites import linear_regression, lstm
from machine_learning.model_features import feature_1, feature_2
from machine_learning.model_analysis import metric_1

###################################################################################################
###################################################################################################

def IMPLEMENTED_MODELS() -> dict:
    return {
        'linear_regression': linear_regression.create_model_suite,
        'lstm': lstm.create_model_suite,
    }

def IMPLEMENTED_FEATURES() -> dict:
    return {
        'feature_1': feature_1.create_feature_suite,
        'feature_2': feature_2.create_feature_suite,
    }

def IMPLEMENTED_METRICS() -> dict:
    return {
        'metric_1': metric_1.create_metric_suite
    }
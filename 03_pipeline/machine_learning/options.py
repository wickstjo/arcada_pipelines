from machine_learning.model_suites import linear_regression, lstm, cnn
from machine_learning.model_features import feature_1, feature_2
from machine_learning.model_analysis import probe_1

###################################################################################################
###################################################################################################

def IMPLEMENTED_MODELS() -> dict:
    return {
        'linear_regression': linear_regression.create_model_suite,
        'lstm': lstm.create_model_suite,
        'cnn': cnn.create_model_suite,
    }

def IMPLEMENTED_FEATURES() -> dict:
    return {
        'feature_1': feature_1.create_feature_suite,
        'feature_2': feature_2.create_feature_suite,
    }

def IMPLEMENTED_PROBES() -> dict:
    return {
        'probe_1': probe_1.create_probe_suite
    }
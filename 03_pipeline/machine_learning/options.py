from machine_learning.model_suites import linreg_model, lstm_model, cnn_model
from machine_learning.model_features import shifting_column
from machine_learning.model_analysis import rmse

###################################################################################################
###################################################################################################

def IMPLEMENTED_MODELS() -> dict:
    return {
        'linreg': linreg_model.create_model_suite,
        'lstm': lstm_model.create_model_suite,
        'cnn': cnn_model.create_model_suite,
    }

def IMPLEMENTED_FEATURES() -> dict:
    return {
        'shifting_column': shifting_column.create_feature_suite
    }

def IMPLEMENTED_PROBES() -> dict:
    return {
        'rmse': rmse.create_probe_suite
    }
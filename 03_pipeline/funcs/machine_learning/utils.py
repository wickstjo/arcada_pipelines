from funcs.machine_learning import linreg_model, lstm_model, cnn_model

# PIPELINE COMPONENTS THAT USE THESE MODELS INHERIT THIS WHITELIST
# MODIFY IT WHEN YOU HAVE IMPLEMENTED SOMETHING TO ENABLE THE MODEL TYPE
# KAFKA EVENTS ALWAYS PASS IN THE MODEL STRING TYPE IN LOWERCASE

def IMPLEMENTED_MODELS():
    return {
        'linreg': linreg_model.create_model_suite,
        'lstm': lstm_model.create_model_suite,
        'cnn': cnn_model.create_model_suite,
    }
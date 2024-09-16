import random

# EXPECTED INPUT/OUTPUT FOR KAFKA/CASSANDRA
# USED BY misc.validate_dict

###################################################################################################
###################################################################################################

# WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
REFINED_STOCK_DATA: dict = {
    'timestamp': lambda x: int(random.uniform(10**3, 10**6)),
    'high': float,
    'low': float,
    'open': float,
    'close': float,
    'volume': lambda x: int(float(x)),
}

# WHAT MODEL INFO SHOULD PIPELINE COMPONENTS PASS TO EACH OTHER?
# IN ORDER TO BOOT IT UP ON THE RECEIVING END?
MODEL_INFO: dict = {
    'uuid': lambda x: x,
    'timestamp': int,
    'model_type': str,
    'model_name': str,
    'model_version': str,
    'model_filename': str,
    'active_status': bool,
}

# WHAT SHOULD A MODEL TRAINING REQUEST CONTAIN?
ANALYSIS_REQUEST: dict = {
    'uuid': lambda x: x,
    'timestamp': int,
    'model_type': str,
    'model_name': str,
    'model_version': str,
    'model_filename': str,
}

# WHAT SHOULD A MODEL TRAINING REQUEST CONTAIN?
TRAINING_REQUEST: dict = {
    'predecessor': lambda x: x, # UUID OR FALSE
    'model_type': str,
    'model_name': str,
    'model_version': str,
}

# WERE GOING TO MAKE A FINAL DECISION BASED ON MULTIPLE MODELS' PREDICTION OUTPUT.
# WHAT SHOULD THE BATCH DATA LOOK LIKE?
PREDICTION_BATCH: dict = {
    'input_row': dict,
    'predictions': dict
}
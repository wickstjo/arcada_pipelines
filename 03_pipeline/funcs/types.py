import time
from datetime import datetime


# EXPECTED INPUT/OUTPUT FOR KAFKA/CASSANDRA
# USED BY misc.validate_dict

###################################################################################################
###################################################################################################

# CONVERT STRING TEXT TO UNIX TIMESTAMP
def string_to_unix(date_text: str) -> int:
    date_tuple = datetime.strptime(date_text, '%Y-%m-%d')
    return int(time.mktime(date_tuple.timetuple()))

# WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
REFINED_STOCK_DATA: dict = {
    'symbol': str,
    'timestamp': string_to_unix,
    'high': float,
    'low': float,
    'open': float,
    'close': float,
    'adjusted_close': float,
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
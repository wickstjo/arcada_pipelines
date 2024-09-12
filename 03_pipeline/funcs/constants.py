import random
from dataclasses import dataclass, field
from funcs.machine_learning import linreg_model, lstm_model, cnn_model

###################################################################################################
###################################################################################################

# KAFKA MQ TOPICS
@dataclass(frozen=True)
class kafka:
    DATA_REFINERY: str = 'data_refinery'
    MODEL_TRAINING: str = 'model_training'
    MODEL_INFERENCE: str = 'model_inference'
    MODEL_ANALYSIS: str = 'model_analysis'
    DECISION_SYNTHESIS: str = 'decision_synthesis'

###################################################################################################
###################################################################################################

# CASSANDRA DB TABLES
@dataclass(frozen=True)
class cassandra:
    STOCKS_TABLE: str = 'dev.refined_stock_data'
    MODELS_TABLE: str = 'dev.model_history'

###################################################################################################
###################################################################################################

# DATA TYPES FOR INPUT/OUTPUT VALIDATION
# USED BY misc.validate_dict
@dataclass(frozen=True)
class types:

    # WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
    REFINED_STOCK_DATA: dict = field(default_factory={
        'timestamp': lambda x: int(random.uniform(10**3, 10**6)),
        'high': float,
        'low': float,
        'open': float,
        'close': float,
        'volume': lambda x: int(float(x)),
    })

    # WHAT MODEL INFO SHOULD PIPELINE COMPONENTS PASS TO EACH OTHER?
    # IN ORDER TO BOOT IT UP ON THE RECEIVING END?
    MODEL_INFO: dict = field(default_factory={
        'model_type': str,
        'model_filename': str,
    })

    # WHAT SHOULD A MODEL TRAINING REQUEST CONTAIN?
    MODEL_TRAINING_REQUEST: dict = field(default_factory={
        'model_name': str,
        'model_type': lambda x: str(x).lower(),
        'dataset_rows': int,
    })

    # WERE GOING TO MAKE A FINAL DECISION BASED ON MULTIPLE MODELS' PREDICTION OUTPUT.
    # WHAT SHOULD THE BATCH DATA LOOK LIKE?
    PREDICTION_BATCH: dict = field(default_factory={
        'input_row': dict,
        'predictions': dict
    })

###################################################################################################
###################################################################################################

# PIPELINE COMPONENTS THAT USE THESE MODELS INHERIT THIS WHITELIST
# MODIFY IT WHEN YOU HAVE IMPLEMENTED SOMETHING TO ENABLE THE MODEL TYPE
# KAFKA EVENTS ALWAYS PASS IN THE MODEL STRING TYPE IN LOWERCASE

def IMPLEMENTED_MODELS() -> dict:
    return {
        'linreg': linreg_model.create_model_suite,
        'lstm': lstm_model.create_model_suite,
        'cnn': cnn_model.create_model_suite,
    }
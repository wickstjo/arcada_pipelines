import json, os
import funcs.misc as misc

########################################################################################################
########################################################################################################

# PIPELINE COMPONENTS THAT USE THESE MODELS INHERIT THIS WHITELIST
# MODIFY IT WHEN YOU HAVE IMPLEMENTED SOMETHING TO ENABLE THE MODEL TYPE
# KAFKA EVENTS ALWAYS PASS IN THE MODEL STRING TYPE IN LOWERCASE

def IMPLEMENTED_MODELS():
    return {
        'lstm': create_lstm_suite,
        'cnn': create_cnn_suite,
        'linreg': create_linreg_suite,
    }

########################################################################################################
########################################################################################################

# LINEAR REGRESSION
class create_linreg_suite:
    def __init__(self):
        self.model = None

    ########################################################################################################
    ########################################################################################################

    # PERFORM THE SAME FEATURE ENGINEERING DURING TRAINING & INFERENCE
    def create_features(self, input_data: dict):
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE TRAIN A NEW MODEL?
    def train_and_save(self, dataset: list[dict], model_id: str) -> None:
        model_path = f'./models/{model_id}.json'

        # MAKE SURE MODEL NAME DOESNT EXIST
        if os.path.isfile(model_path): raise Exception(f'TRAINING ERROR: MODEL NAME ({model_path}) ALREADY EXISTS')

        with open(model_path, 'w') as file:
            json.dump({ 'foo': dataset }, file)

        misc.log(f'LOADED TRAINED ({model_path})')

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE LOAD A TRAINED MODEL FROM A FILE?
    def load_model(self, model_id: str) -> None:
        model_path = f'./models/{model_id}.json'

        # VALIDATE STATE
        if self.model is not None: raise Exception('LOAD ERROR: A MODEL HAS ALREADY BEEN LOADED')
        if not os.path.isfile(model_path): raise Exception(f'LOAD ERROR: MODEL ({model_path}) DOES NOT EXIST')

        # FINALLY, LOAD THE MODEL TO STATE
        with open(model_path) as file:
            self.model = json.load(file)

        misc.log(f'LOADED MODEL ({model_path})')

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE GENERATE A MODEL PREDICTION?
    def predict_outcome(self, input_data: dict):
        if self.model is None: raise Exception('PREDICT ERROR: LOAD A MODEL FIRST')
        return True
    
    ########################################################################################################
    ########################################################################################################

    # PERFORM ANALYSIS AND DECIDE WHETHER TO RE-TRAIN A NEW MODEL
    # TO TRIGGER RE-TRAIN, RETURN TRUE, ELSE FALSE
    def analyze_model(self, model_id: str) -> bool:
        
        # LOAD THE MODEL
        self.load_model(model_id)
        
        # TODO: ANALYZE
        return True

########################################################################################################
########################################################################################################

# LONG-SHORT-TERM MEMORY
class create_lstm_suite(create_linreg_suite):
    def __init__(self):
        pass

# CONVOLUTIONAL NEURAL NETWORK
class create_cnn_suite(create_linreg_suite):
    def __init__(self):
        pass


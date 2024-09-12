from typing import Any
import funcs.misc as misc

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_model_suite:
    def __init__(self):
        self.model = None

    ########################################################################################################
    ########################################################################################################

    # PERFORM THE SAME FEATURE ENGINEERING DURING TRAINING & INFERENCE
    def create_features(self, input_data: dict) -> Any:
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE TRAIN A NEW MODEL?
    # AT THE END, SAVE THE FILE TO THE FILESYSTEM
    def train_model(self, dataset: list[dict], model_id: str) -> None:
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE LOAD A TRAINED MODEL FROM A FILE?
    def load_model(self, model_id: str) -> None:
        if self.model is not None: raise Exception('LOAD ERROR: A MODEL HAS ALREADY BEEN LOADED')
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE GENERATE A MODEL PREDICTION?
    def predict_outcome(self, input_data: dict) -> Any:
        if self.model is None: raise Exception('PREDICT ERROR: LOAD A MODEL FIRST')
        pass
    
    ########################################################################################################
    ########################################################################################################

    # PERFORM ANALYSIS AND DECIDE WHETHER TO RE-TRAIN A NEW MODEL
    # TO TRIGGER RE-TRAIN, RETURN TRUE, ELSE FALSE
    def analyze_model(self, model_id: str) -> bool:
        pass
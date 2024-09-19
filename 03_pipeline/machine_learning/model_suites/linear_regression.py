from typing import Any
import funcs.misc as misc
import random

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_model_suite:
    def __init__(self):
        self.model = None

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE TRAIN A NEW MODEL?
    # AT THE END, SAVE THE FILE TO THE FILESYSTEM
    def train_model(self, model_name: str, model_params: dict) -> None:
        misc.log('[MOCK]: TRAINED LINEAR REGRESSION MODEL')
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE LOAD A TRAINED MODEL FROM A FILE?
    def load_model(self, model_name: str) -> None:
        misc.log('[MOCK]: LOADED LINEAR REGRESSION MODEL')
        pass

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE GENERATE A MODEL PREDICTION?
    def predict_outcome(self, input_data: dict) -> Any:
        misc.log('[MOCK]: PREDICTED OUTCOME')
        return random.uniform(0, 100)
from typing import Any
import funcs.misc as misc
import funcs.constants as constants
import random

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_model_suite:
    def __init__(self):
        self.model = None

    ########################################################################################################
    ########################################################################################################

    def train_model(self, model_name: str, segmented_dataset: dict, training_config: dict) -> None:
        misc.log('[MOCK]: TRAINED LINEAR_REGRESSION MODEL')
        misc.save_yaml(f'{constants.dirs.MODEL_REPO}/{model_name}.yml', {})
        pass

    ########################################################################################################
    ########################################################################################################

    def load_model(self, model_name: str) -> None:
        misc.log('[MOCK]: LOADED LINEAR_REGRESSION MODEL')
        self.model = misc.load_yaml(f'{constants.dirs.MODEL_REPO}/{model_name}.yml', {})
        pass

    ########################################################################################################
    ########################################################################################################

    def predict_outcome(self, input_data: dict) -> Any:
        misc.log('[MOCK]: PREDICTED LINEAR_REGRESSION OUTCOME')
        return random.uniform(0, 100)
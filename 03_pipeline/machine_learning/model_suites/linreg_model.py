import json, os
from typing import Any
import funcs.misc as misc

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_model_suite:
    def __init__(self):
        self.model = None
        self.required_dataset_size = 0

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE TRAIN A NEW MODEL?
    # AT THE END, SAVE THE FILE TO THE FILESYSTEM
    def train_model(self, dataset: list[dict], model_id: str) -> None:
        model_path = f'./model_repo/{model_id}.json'

        # MAKE SURE MODEL NAME DOESNT EXIST
        if os.path.isfile(model_path):
            raise Exception(f'TRAINING ERROR: MODEL NAME ({model_path}) ALREADY EXISTS')

        with open(model_path, 'w') as file:
            json.dump({ 'foo': dataset }, file)

    ########################################################################################################
    ########################################################################################################

    # HOW DO WE LOAD A TRAINED MODEL FROM A FILE?
    def load_model(self, model_id: str) -> None:
        model_path = f'./model_repo/{model_id}.json'

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
    def predict_outcome(self, input_data: dict) -> Any:
        if self.model is None: raise Exception('PREDICT ERROR: LOAD A MODEL FIRST')
        return True
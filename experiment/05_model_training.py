import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT

########################################################################################
########################################################################################

config = DICT_NAMESPACE({
    'input_topic': 'model_training',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT):
    pass

    ### TODO: IMPLEMENT SOME PSEUDO MODEL TRAINING
    ### TO TRAIN DIFFERENT MODELS, MAYBE USE SOME TYPE OF SWITCH STATEMENT?

########################################################################################
########################################################################################

kafka_clients.start_consumer(
    config.input_topic, handle_event
)
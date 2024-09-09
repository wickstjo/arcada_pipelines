import utils.kafka_utils as kafka_utils
from utils.types import TO_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC, CASSANDRA_INSTANCE, NAMESPACE

import os

########################################################################################
########################################################################################

local_config = TO_NAMESPACE({

    # KAFKA TOPICS
    'input_topic': 'data_dispatch',
    'model_training_topic': 'model_training',
    'model_inference_topic': 'model_inference',

    # FILE PATHS
    'models_path': './files/models'
})

# DYNAMIC STATE
state = {
    'received_events': 0,
    'models': os.listdir(local_config.models_path),
}

########################################################################################
########################################################################################

def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC, cassandra: CASSANDRA_INSTANCE, global_config: NAMESPACE):
    
    # INCREMENT RECEIVED EVENTS
    state['received_events'] += 1

    if (state['received_events'] % 5) == 0:
        state['models'] = os.listdir(local_config.models_path)

    # CHECK MODEL DIR FOR WHAT MODELS ARE CURRENTLY TRAINED
    # EVERY 10 (?) EVENTS, CHECK DIR AGAIN

            # WE HAVE NO MODELS
                # READ YAML FOR HOW MANY ROWS ARE NECESSARY TO TRAIN A MODEL
                # START COUNTING INCOMING ROWS
                # WHEN THRESHOLD IS MET, SEND EVENT TO MODEL_TRAINING

            # WE HAVE MODELS
                # FORWARD DATA TO EACH ONE
                # WHAT IF A SYSTEM IS FRESHLY BOOTED UP, BUT WE HAVE SOME TRAINED MODELS ALREADY?

########################################################################################
########################################################################################

kafka_utils.start_flex_consumer(
    local_config.input_topic,
    handle_event,

    # DO YOU NEED A KAFKA PRODUCER OR CASSANDRA CLIENT?
    # REMEMBER TO ADD/REMOVE THEM AS INPUT ARGS TO handle_events ^
    include_kafka_push=True,
    include_cassandra=True,
    include_config=True,
)
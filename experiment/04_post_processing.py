import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # RELEVANT KAFKA TOPICS
    'input_topic': 'post_processing',
    'training_topic': 'model_training',
    'tracker_topic': 'model_tracker',

    # DEFINE THE DATABASE QUERY FOR INJECTION
    'db_insert_query': 'INSERT INTO test_keyspace.test_table (timestamp, open, close, high, low, volume) values (?, ?, ?, ?, ?, ?);',

    # DEFINE A DRIFT THRESHOLD FOR WHEN NEW MODELS SHOULD BE TRAINED
    'retrain_drift_threshold': 0.7
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):

    ### TODO: CHECK INPUT PROPS
    ### TODO: WRITE PREDICTIONS TO DATABASE

    ### TODO: CONDITIONALLY, MEASURE MODEL DRIFT
    ### TODO: ALWAYS SEND DRIFT MEASUREMENTS TO THE MODEL TRACKING TOPIC

    # PUSH REQUEST TO A LIVE-TRACKING TOPIC
    kafka_push(config.tracker_topic, {

        # WHAT SOURCE (MODEL?) SHOULD THIS DATA BE LINKED TO?
        'source': 'model_temp',
        'output': {

            # WHAT INFORMATION DO WE WANT TO LIVE TRACK?
            'model_prediction': 'temp',
            'model_drift': 'temp',
            'something_else': 'temp',
        }
    })

    ### TODO: IF DRIFT >= THRESHOLD, PUSH "RE-TRAIN" REQUEST TO KAFKA
    ### MAYBE THIS CODE SHOULD CONTACT THE MODEL REPO FOR THE ORIGINAL CONFIG?

    # PUSH REQUEST TO A TRAINING TOPIC
    kafka_push(config.training_topic, {

        # EACH MODEL SHOULD PROBABLY HAVE A UNIQUE NAME?
        'model_name': 'temp',

        # USE A DATABASE TABLE AS INPUT?
        'database': {
            'table_name': 'temp',
            'start': 'temp',
            'end': 'temp',
            'validation_percent': 20,
        },

        # USE KAFKA STREAM AS INPUT?
        # MAYBE SAVE THIS FOR MODEL COMPARISON PIPELINES?
        'stream': {
            'topic': 'temp'
        }
    })

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
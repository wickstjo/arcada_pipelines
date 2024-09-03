import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # RELEVANT KAFKA TOPICS
    'input_topic': 'post_processing',
    'training_topic': 'model_training',
    'tracker_topic': 'drift_tracker',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    print(input_data)

    kafka_push(config.training_topic, input_data)
    kafka_push(config.tracker_topic, input_data)

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

config = DICT_NAMESPACE({
    'input_topic': 'input_data',
    'output_topic': 'model_usage',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    pass

    ### THIS ONLY MAKES SENSE FOR STREAM PROCESSING
    ### TODO: DEVELOP SOMETHING SIMILAR FOR MASS-SCALE BATCH PROCESSING

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
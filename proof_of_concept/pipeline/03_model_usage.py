import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # KAFKA TOPICS
    'input_topic': 'model_usage',
    'output_topic': 'post_processing',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    print(input_data)
    kafka_push(config.output_topic, input_data)

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
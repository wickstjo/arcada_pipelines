import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

config = DICT_NAMESPACE({
    'input_topic': 'model_evaluation',
    'training_topic': 'model_training',
    'stats_topic': 'model_stats',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    print(input_data)

    # PUSH REQUEST TO A TRAINING TOPIC
    kafka_push(config.training_topic, {
        'foo': 'bar'
    })

    ### DO STUFF HERE
    ### DO STUFF HERE
    ### DO STUFF HERE

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
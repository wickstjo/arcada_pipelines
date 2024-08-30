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
    print(input_data)

    ### DO STUFF HERE
    ### DO STUFF HERE
    ### DO STUFF HERE

########################################################################################
########################################################################################

kafka_clients.start_consumer(
    config.input_topic, handle_event
)
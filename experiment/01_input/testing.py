import utilz.kafka_clients as kafka_clients
from typing import Dict, Any

########################################################################################
########################################################################################

# HANDLE EVENTS FROM THE KAFKA INPUT_TOPIC
# RETURN VALUE (DICT) IS PUSHED TO THE OUTPUT_TOPIC
def handle_event(input_data: Dict[str, Any]) -> Dict[str, Any]:
    print(input_data)

    ### DO STUFF
    ### DO STUFF
    ### DO STUFF

    return {
        'foo': 'bar'
    }

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer({
    'input_topic': 'model_usage',
    'output_topic': 'model_evaluation',
}, handle_event)
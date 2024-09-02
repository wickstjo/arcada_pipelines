import utilz.kafka_clients as kafka_clients
from utilz.prometheus_utils import create_prometheus_endpoint
from utilz.types import DICT_NAMESPACE, KAFKA_DICT

########################################################################################
########################################################################################

config = DICT_NAMESPACE({
    'input_topic': 'model_tracker',

    # WHAT PORT SHOULD THE PROMETHEUS SCRAPING SERVER RUN ON?
    'prometheus_port': 8282,
})

# CREATE A PROMETHEUS ENDPOINT FOR AUTO-SCRAPING
prometheus = create_prometheus_endpoint(config.prometheus_port)

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT):

    # MAKE SURE BOTH REQUIRED KEYS EXIST
    for key in ['source', 'output']:
        if key not in input_data:
            raise Exception(f'MISSING INPUT KEY ({key})')
    
    # MAKE SURE THE SOURCE NAME DOESNT CONTAIN DOTS
    # CAUSES PROBLEMS FOR PROMETHEUS FOR SOME REASON
    # TODO: FIGURE OUT WHAT THE NAMING RULESET IS EXACTLY
    if (input_data['source'].count('.') > 0) or (input_data['source'].count('/') > 0):
        raise Exception(f"FAULTY SOURCE NAME ({input_data['source']})")

    # OTHERWISE, EVERYTHING SEEMS FINE
    # PUBLISH THE RESULTS TO THE PROMETHEUS ENDPOINT
    prometheus.push_metric(input_data)

########################################################################################
########################################################################################

kafka_clients.start_consumer(
    config.input_topic, handle_event
)
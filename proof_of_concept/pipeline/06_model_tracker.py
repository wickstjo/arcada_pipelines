import utilz.kafka_clients as kafka_clients
# from utilz.prometheus_utils import create_prometheus_endpoint
from utilz.types import DICT_NAMESPACE, KAFKA_DICT

########################################################################################
########################################################################################

config = DICT_NAMESPACE({
    'input_topic': 'drift_tracker',

    # WHAT PORT SHOULD THE PROMETHEUS SCRAPING SERVER RUN ON?
    'prometheus_port': 8282,
})

# CREATE A PROMETHEUS ENDPOINT FOR AUTO-SCRAPING
# prometheus = create_prometheus_endpoint(config.prometheus_port)

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT):
    print(input_data)

########################################################################################
########################################################################################

kafka_clients.start_consumer(
    config.input_topic, handle_event
)   
import utils.kafka_utils as kafka_utils
# from utilz.prometheus_utils import create_prometheus_endpoint
from utils.misc import DICT_NAMESPACE
from utils.types import KAFKA_DICT

########################################################################################
########################################################################################

local_config = DICT_NAMESPACE({
    'input_topic': 'drift_tracker',

    # WHAT PORT SHOULD THE PROMETHEUS SCRAPING SERVER RUN ON?
    # 'prometheus_port': 8282,
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

kafka_utils.start_consumer(
    local_config.input_topic, handle_event
)
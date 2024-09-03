import utils.kafka_utils as kafka_utils
from utils.misc import DICT_NAMESPACE
from utils.types import KAFKA_DICT

########################################################################################
########################################################################################

local_config = DICT_NAMESPACE({
    'input_topic': 'model_training',
})

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
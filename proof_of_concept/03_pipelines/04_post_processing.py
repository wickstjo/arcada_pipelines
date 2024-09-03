import utils.kafka_utils as kafka_utils
from utils.misc import DICT_NAMESPACE
from utils.types import KAFKA_DICT, KAFKA_PUSH_FUNC

########################################################################################
########################################################################################

local_config = DICT_NAMESPACE({
    'input_topic': 'post_processing',
    'training_topic': 'model_training',
    'tracker_topic': 'drift_tracker',
})

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    print(input_data)

    kafka_push(local_config.training_topic, input_data)
    kafka_push(local_config.tracker_topic, input_data)

########################################################################################
########################################################################################

kafka_utils.start_consumer_producer(
    local_config.input_topic, handle_event
)
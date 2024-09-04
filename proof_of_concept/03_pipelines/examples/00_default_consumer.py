import utils.kafka_utils as kafka_utils
from utils.types import TO_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC, CASSANDRA_INSTANCE
from utils.misc import load_global_config

########################################################################################
########################################################################################

# LOAD THE GLOBAL CONFIG
global_config = load_global_config()

# WHAT PARAMS ONLY RELEVANT FOR THIS COMPONENT?
local_config = TO_NAMESPACE({
    'input_topic': 'foo',
    'output_topic': 'bar',
})

########################################################################################
########################################################################################

def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC, cassandra: CASSANDRA_INSTANCE):
    print(input_data)
    kafka_push(local_config.output_topic, input_data)

########################################################################################
########################################################################################

kafka_utils.start_flex_consumer(
    local_config.input_topic,
    handle_event,

    # DO YOU NEED A KAFKA PRODUCER OR CASSANDRA CLIENT?
    # REMEMBER TO ADD/REMOVE THEM AS INPUT ARGS TO handle_events ^
    include_kafka_push=True,
    include_cassandra=True
)
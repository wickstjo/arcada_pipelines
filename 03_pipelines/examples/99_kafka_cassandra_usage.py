import utils.kafka_utils as kafka_utils
from utils.types import KAFKA_DICT, KAFKA_PUSH_FUNC, CASSANDRA_INSTANCE, TO_NAMESPACE

########################################################################################
########################################################################################

local_config = TO_NAMESPACE({

    # KAFKA TOPICS
    'input_topic': 'my_input_data',
    'output_topic': 'my_output_data',

    # CASSANDRA TABLES
    'data_table': 'my_input_data',
    'results_table': 'my_output_data',
})

########################################################################################
########################################################################################

def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC, cassandra: CASSANDRA_INSTANCE):

    # READ FROM A CASSANDRA TABLE
    results = cassandra.read(f'SELECT * FROM {local_config.data_table}')

    # WRITE TO A CASSANDRA TABLE
    cassandra.write(local_config.results_table, {
        'foo': 'bar',
        'biz': 'baz'
    })

    # PUSH DATA TO A OUTPUT TOPIC
    kafka_push(local_config.output_topic, {
        'one': 'two',
        'three': 'four'
    })

########################################################################################
########################################################################################

kafka_utils.start_flex_consumer(
    local_config.input_topic,
    handle_event,

    # DO YOU NEED A KAFKA PRODUCER OR CASSANDRA CLIENT?
    # REMEMBER TO ADD THEM AS INPUT ARGS TO handle_events
    include_kafka_push=True,
    include_cassandra=True
)
import utils.kafka_utils as kafka_utils
import utils.misc as misc
import random

########################################################################################
########################################################################################

class create_state:
    def __init__(self):

        # RELEVANT KAFKA TOPICS
        self.input_topic: str = 'data_refinery'
        self.output_topic: str = 'data_dispatch'

        # WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
        self.ref_stock_data = {
            'timestamp': lambda x: int(random.uniform(10**3, 10**6)),
            'high': float,
            'low': float,
            'open': float,
            'close': float,
            'volume': lambda x: int(float(x)),
        }
    
        # CASSANDRA TABLE FOR STORING REFINED DATA
        self.cassandra_table: str = 'refined.stock_data'

state = create_state()

########################################################################################
########################################################################################

def handle_event(kafka_topic: str, kafka_input: dict, support_structs: list):

    # EXTRACT THE SUPPORT STRUCTS -- ORDER: (KAFKA_PRODUCER, CASSANDRA, GLOBAL_CONFIG)
    kafka_producer, cassandra = support_structs

    # ATTEMPT TO VALIDATE DICT AGAINST REFERENCE OBJECT
    valid_row: dict = misc.validate_dict(kafka_input, state.ref_stock_data)
    misc.log('[HANDLE_EVENTS] ROW PASSED VALIDATION')

    # VALIDATION SUCCEEDED, WRITE THE ROW TO DB
    # AND PUSH IT TO KAFKA DISPATCH
    cassandra.write(state.cassandra_table, valid_row)
    kafka_producer.push_msg(state.output_topic, valid_row)

########################################################################################
########################################################################################

kafka_utils.start_flex_consumer(
    state.input_topic,
    handle_event,

    # DOES YOUR FUNCTION NEED A KAFKA PRODUCER, CASSANDRA CLIENT OR THE YAML CONFIG?
    # REMEMBER TO ADD/REMOVE THEM AS INPUT ARGS TO handle_events ^
    # KEEP THIS ORDER!
    include_kafka_producer=True,
    include_cassandra=True,
    # include_yaml_config=True,
)
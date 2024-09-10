from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import random

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.cassandra = create_cassandra_instance()
        self.kafka_producer = create_kafka_producer()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str = 'data_refinery'
        self.output_topic: str = 'data_dispatch'

        # WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
        self.stock_data_type: dict = {
            'timestamp': lambda x: int(random.uniform(10**3, 10**6)),
            'high': float,
            'low': float,
            'open': float,
            'close': float,
            'volume': lambda x: int(float(x)),
        }
    
        # CASSANDRA TABLE FOR STORING REFINED DATA
        self.cassandra_table: str = 'refined.stock_data'

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def handle_event(self, kafka_topic: str, kafka_input: dict):

        # ATTEMPT TO VALIDATE DICT AGAINST REFERENCE OBJECT
        valid_row: dict = misc.validate_dict(kafka_input, self.stock_data_type)
        misc.log('ROW PASSED VALIDATION')

        # VALIDATION SUCCEEDED, WRITE THE ROW TO DB
        # AND PUSH IT TO KAFKA DISPATCH
        self.cassandra.write(self.cassandra_table, valid_row)
        self.kafka_producer.push_msg(self.output_topic, valid_row)

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
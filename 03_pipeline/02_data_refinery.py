from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import funcs.constants as constants
import funcs.types as types

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE INSTANCED CLIENTS
        self.cassandra = create_cassandra_instance()
        self.kafka_producer = create_kafka_producer()

        # WHAT KAFKA TOPIC DO YOU WANT TO CONSUME DATA FROM?
        self.kafka_input_topics: str|list[str] = constants.kafka.DATA_REFINERY

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # ATTEMPT TO VALIDATE DICT AGAINST REFERENCE OBJECT
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)
        misc.log('ROW PASSED VALIDATION')

        # VALIDATION SUCCEEDED, WRITE THE ROW TO DB
        # AND PUSH REFINED DATA BACK TO KAFKA
        self.cassandra.write(constants.cassandra.STOCKS_TABLE, refined_stock_data)
        self.kafka_producer.push_msg(constants.kafka.MODEL_INFERENCE, refined_stock_data)

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
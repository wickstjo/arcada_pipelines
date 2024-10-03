from funcs import kafka_utils, cassandra_utils
from funcs import thread_utils, misc, constants, types

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.cassandra = cassandra_utils.create_instance()
        self.kafka = kafka_utils.create_instance()

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DATA_REFINERY, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # ATTEMPT TO VALIDATE DICT AGAINST REFERENCE OBJECT
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)
        misc.log('[COMPONENT] ROW PASSED VALIDATION')

        # VALIDATION SUCCEEDED, WRITE THE ROW TO DB
        # AND PUSH REFINED DATA BACK TO KAFKA
        self.cassandra.write(constants.cassandra.STOCKS_TABLE, refined_stock_data)
        self.kafka.push(constants.kafka.MODEL_DISPATCH, refined_stock_data)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
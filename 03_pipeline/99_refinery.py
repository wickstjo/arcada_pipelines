from funcs import kafka_utils, redis_utils, cassandra_utils
from funcs import thread_utils, misc, constants, types

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, process_beacon):

        # CREATE INSTANCED CLIENTS
        self.cassandra = cassandra_utils.create_instance()
        self.kafka = kafka_utils.create_instance()
        self.redis = redis_utils.create_instance()

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DATA_REFINERY, self.on_kafka_event, process_beacon)
        self.redis.subscribe(constants.redis.MODEL_PIPELINES, self.on_redis_event, process_beacon)

########################################################################################
########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # ATTEMPT TO VALIDATE DICT AGAINST REFERENCE OBJECT
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)
        misc.log('[KAFKA CALLBACK] ROW PASSED VALIDATION')

        # VALIDATION SUCCEEDED, WRITE THE ROW TO DB
        # AND PUSH REFINED DATA BACK TO KAFKA
        self.cassandra.write(constants.cassandra.STOCKS_TABLE, refined_stock_data)
        self.kafka.push(constants.kafka.MODEL_INFERENCE, refined_stock_data)

########################################################################################
########################################################################################

    def on_redis_event(self):
        misc.log('[REDIS CALLBACK] TRIGGER')

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
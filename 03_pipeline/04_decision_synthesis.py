from funcs import kafka_utils, redis_utils, cassandra_utils, mlflow_utils
from funcs import thread_utils, misc, constants
import json

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, thread_beacon):

        # CREATE INSTANCED CLIENTS
        self.cassandra = cassandra_utils.create_instance()
        self.kafka = kafka_utils.create_instance()
        self.redis = redis_utils.create_instance()
        self.mlflow = mlflow_utils.create_instance()

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DECISION_SYNTHESIS, self.on_kafka_event, thread_beacon)
        self.redis.subscribe(constants.redis.MODEL_PIPELINES, self.on_redis_change, thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        misc.log('[COMPONENT] RECEIVED PREDICTION BATCH')
        print(json.dumps(kafka_input, indent=4))

        # {
        #     'input_row': {
        #         'timestamp': 1727460997, 
        #         'symbol': AAPL, 
        #         'open': 160.02000427246094, 
        #         'high': 162.3000030517578, 
        #         'low': 154.6999969482422, 
        #         'close': 161.6199951171875, 
        #         'adjusted_close': 159.1901397705078, 
        #         'volume': 162294600
        #     }, 
        #     'predictions': {
        #         'pipe_4': 'input_row -> [model_6, v_champion]', 
        #         'pipe_5': 'input_row -> [model_7, v_champion] -> [model_8, v_champion]'
        #     }
        # }
    
    ########################################################################################
    ########################################################################################

    def on_redis_change(self, latest_value: dict):
        pass

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
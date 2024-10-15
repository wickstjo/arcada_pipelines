from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('POST_PROCESSING')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.POST_PROCESSING, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('COMPLETE LIFECYCLE', kafka_input) as span:

            with self.jaeger.create_span('MEASURE MODEL_1 DRIFT', span) as span:
                misc.timeout_range(0.1, 0.15)
        
            with self.jaeger.create_span('MEASURE MODEL_2 DRIFT', span) as span:
                misc.timeout_range(0.1, 0.15)

            with self.jaeger.create_span('LARGE DRIFT: FLAG MODEL FOR RE-TRAINING', span) as span:
                misc.timeout_range(0.05, 0.1)
        
            with self.jaeger.create_span('MEASURE MODEL_3 DRIFT', span) as span:
                misc.timeout_range(0.1, 0.15)

            with self.jaeger.create_span('MEASURE MODEL_4 DRIFT', span) as span:
                misc.timeout_range(0.1, 0.15)

            with self.jaeger.create_span('MEASURE MODEL_5 DRIFT', span) as span:
                misc.timeout_range(0.1, 0.15)

            with self.jaeger.create_span('LARGE DRIFT: FLAG MODEL FOR RE-TRAINING', span) as span:
                misc.timeout_range(0.05, 0.1)

            with self.jaeger.create_span('MEASURE DATA DRIFT', span) as span:
                misc.timeout_range(0.20, 0.30)

            with self.jaeger.create_span('MEASURE CONCEPT DRIFT', span) as span:
                misc.timeout_range(0.20, 0.30)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('post_processing')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.POST_PROCESSING, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        def first():
            with self.jaeger.create_span('MEASURE MODEL_1 DRIFT', kafka_input) as span:
                misc.timeout_range(0.1, 0.15)
        
        def second():
            with self.jaeger.create_span('MEASURE MODEL_2 DRIFT', kafka_input) as span:
                misc.timeout_range(0.1, 0.15)

            with self.jaeger.create_span('LARGE DRIFT: WRITE RE-TRAINING REQUEST TO DB', span) as span:
                misc.timeout_range(0.20, 0.30)
        
        def third():
            with self.jaeger.create_span('MEASURE MODEL_3 DRIFT', kafka_input) as span:
                misc.timeout_range(0.1, 0.15)

                # parent.log_kv({
                #     'event': 'error', 
                #     'message': 'An error occurred', 
                #     'error.code': 500
                # })

        def fourth():
            with self.jaeger.create_span('MEASURE DATA DRIFT', kafka_input) as span:
                misc.timeout_range(0.20, 0.30)

        def fifth():
            with self.jaeger.create_span('MEASURE CONCEPT DRIFT', kafka_input) as span:
                misc.timeout_range(0.20, 0.30)

        thread_utils.start_thread(first)
        thread_utils.start_thread(second)
        thread_utils.start_thread(third)
        thread_utils.start_thread(fourth)
        thread_utils.start_thread(fifth)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
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
        with self.jaeger.create_span('COMPLETE LIFECYCLE', kafka_input) as true_parent:

            def first():
                with self.jaeger.create_span('MEASURE MODEL_1 DRIFT', true_parent) as span:
                    misc.timeout_range(0.1, 0.15)
            
            def second():
                with self.jaeger.create_span('MEASURE MODEL_2 DRIFT', true_parent) as span:
                    misc.timeout_range(0.1, 0.15)

                with self.jaeger.create_span('LARGE DRIFT: FLAG MODEL FOR RE-TRAINING', span) as span:
                    misc.timeout_range(0.05, 0.1)
            
            def third():
                with self.jaeger.create_span('MEASURE MODEL_3 DRIFT', true_parent) as span:
                    misc.timeout_range(0.1, 0.15)

                    # parent.log_kv({
                    #     'event': 'error', 
                    #     'message': 'An error occurred', 
                    #     'error.code': 500
                    # })

            def fourth():
                with self.jaeger.create_span('MEASURE MODEL_4 DRIFT', true_parent) as span:
                    misc.timeout_range(0.1, 0.15)

            def fifth():
                with self.jaeger.create_span('MEASURE MODEL_5 DRIFT', true_parent) as span:
                    misc.timeout_range(0.1, 0.15)

                with self.jaeger.create_span('LARGE DRIFT: FLAG MODEL FOR RE-TRAINING', span) as span:
                    misc.timeout_range(0.05, 0.1)

            def sixth():
                with self.jaeger.create_span('MEASURE DATA DRIFT', true_parent) as span:
                    misc.timeout_range(0.20, 0.30)

            def seventh():
                with self.jaeger.create_span('MEASURE CONCEPT DRIFT', true_parent) as span:
                    misc.timeout_range(0.20, 0.30)

            t1 = thread_utils.start_thread(first)
            t2 = thread_utils.start_thread(second)
            t3 = thread_utils.start_thread(third)
            t4 = thread_utils.start_thread(fourth)
            t5 = thread_utils.start_thread(fifth)
            t6 = thread_utils.start_thread(sixth)
            t7 = thread_utils.start_thread(seventh)

            t1.join()
            t2.join()
            t3.join()
            t4.join()
            t5.join()
            t6.join()
            t7.join()

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
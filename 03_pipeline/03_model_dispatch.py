from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('MODEL_DISPATCH')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.MODEL_DISPATCH, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('COMPLETE LIFECYCLE', kafka_input) as span:
                
            with self.jaeger.create_span('RUNNING ALL MODEL PIPES', span) as model_parent:
    
                def pipe_1():
                    with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_1', model_parent) as span:
                        misc.timeout_range(0.08, 0.15)

                    with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_2', span) as span:
                        misc.timeout_range(0.08, 0.15)

                    with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_3', span) as span:
                        misc.timeout_range(0.08, 0.15)

                def pipe_2():
                    with self.jaeger.create_span('PIPE_2: PREDICTING WITH MODEL_4', model_parent) as span:
                        misc.timeout_range(0.08, 0.15)

                def pipe_3():
                    with self.jaeger.create_span('PIPE_3: PREDICTING WITH MODEL_5', model_parent) as span:
                        misc.timeout_range(0.08, 0.15)

                thread_1 = thread_utils.start_thread(pipe_1)
                thread_utils.start_thread(pipe_2)
                thread_utils.start_thread(pipe_3)
                thread_1.join()

            def first():
                with self.jaeger.create_span('KAFKA: FORWARDING PREDICTION BATCH', model_parent) as span:
                    misc.timeout_range(0.02, 0.05)

                    trace_context = self.jaeger.create_context(span)
                    self.kafka.push(constants.kafka.DECISION_SYNTHESIS, trace_context)

            def second():
                with self.jaeger.create_span('KAFKA: FORWARDING MODEL META-DATA', model_parent) as span:
                    misc.timeout_range(0.02, 0.05)

                    trace_context = self.jaeger.create_context(span)
                    self.kafka.push(constants.kafka.POST_PROCESSING, trace_context)

            def third():
                with self.jaeger.create_span('DB: SAVING MODEL PREDICTIONS', model_parent) as span:
                    misc.timeout_range(0.05, 0.1)

            t1 = thread_utils.start_thread(first)
            t2 = thread_utils.start_thread(second)
            t3 = thread_utils.start_thread(third)

            t1.join()
            t2.join()
            t3.join()

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
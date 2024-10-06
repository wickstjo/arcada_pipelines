from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('model_dispatch')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.MODEL_DISPATCH, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('PREDICTING WITH MODEL_1', kafka_input) as span:
            misc.timeout_range(0.04, 0.1)

        with self.jaeger.create_span('PREDICTING WITH MODEL_2', span) as span:
            misc.timeout_range(0.04, 0.1)

            # span.set_tag('error', True)

        with self.jaeger.create_span('PREDICTING WITH MODEL_3', span) as parent:
            misc.timeout_range(0.04, 0.1)

            # parent.log_kv({
            #     'event': 'error', 
            #     'message': 'An error occurred', 
            #     'error.code': 500
            # })

            def first():
                with self.jaeger.create_span('WRITING PREDICTION BATCH TO KAFKA', parent) as span:
                    misc.timeout_range(0.1, 0.15)

                    trace_context = self.jaeger.create_context(span)
                    self.kafka.push(constants.kafka.DECISION_SYNTHESIS, trace_context)

            def second():
                with self.jaeger.create_span('WRITING POST_PROCESSING METADATA TO KAFKA', parent) as span:
                    misc.timeout_range(0.1, 0.15)

                    trace_context = self.jaeger.create_context(span)
                    self.kafka.push(constants.kafka.POST_PROCESSING, trace_context)

            def third():
                with self.jaeger.create_span('WRITING PREDICTIONS TO DB', parent) as span:
                    misc.timeout_range(0.20, 0.30)

            thread_utils.start_thread(first)
            thread_utils.start_thread(second)
            thread_utils.start_thread(third)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
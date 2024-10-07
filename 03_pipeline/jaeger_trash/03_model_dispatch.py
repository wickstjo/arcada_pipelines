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

            with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_1', span) as span:
                misc.timeout_range(0.08, 0.15)

            with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_2', span) as span:
                misc.timeout_range(0.08, 0.15)

            with self.jaeger.create_span('PIPE_1: PREDICTING WITH MODEL_3', span) as span:
                misc.timeout_range(0.08, 0.15)

            with self.jaeger.create_span('PIPE_2: PREDICTING WITH MODEL_4', span) as span:
                misc.timeout_range(0.08, 0.15)

            with self.jaeger.create_span('PIPE_3: PREDICTING WITH MODEL_5', span) as span:
                misc.timeout_range(0.08, 0.15)

            with self.jaeger.create_span('DB: SAVING MODEL PREDICTIONS', span) as span:
                misc.timeout_range(0.05, 0.1)

            with self.jaeger.create_span('KAFKA: FORWARDING PREDICTION BATCH', span) as span:
                misc.timeout_range(0.02, 0.05)

                trace_context = self.jaeger.create_context(span)
                self.kafka.push(constants.kafka.DECISION_SYNTHESIS, trace_context)

            with self.jaeger.create_span('KAFKA: FORWARDING MODEL META-DATA', span) as span:
                misc.timeout_range(0.02, 0.05)

                trace_context = self.jaeger.create_context(span)
                self.kafka.push(constants.kafka.POST_PROCESSING, trace_context)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
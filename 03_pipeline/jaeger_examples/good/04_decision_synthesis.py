from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('DECISION_SYNTHESIS')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DECISION_SYNTHESIS, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('COMPLETE LIFECYCLE', kafka_input) as span:

            with self.jaeger.create_span('MAKING BUY/SELL/HOLD DECISION', span) as span:
                misc.timeout_range(0.15, 0.25)

            with self.jaeger.create_span('DB: SAVE DECISION', span) as span:
                misc.timeout_range(0.05, 0.1)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
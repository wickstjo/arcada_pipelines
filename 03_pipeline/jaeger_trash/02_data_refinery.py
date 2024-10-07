from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('DATA_REFINERY')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DATA_REFINERY, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('COMPLETE LIFECYCLE') as span:
            
            with self.jaeger.create_span('REFINING STOCK DATA', span) as span:
                misc.timeout_range(0.03, 0.08)

            with self.jaeger.create_span('DB: SAVING STOCK DATA', span) as span:
                misc.timeout_range(0.05, 0.1)

            with self.jaeger.create_span('KAFKA: FORWARDED STOCK DATA TO DISPATCHER', span) as span:
                misc.timeout_range(0.02, 0.05)

                trace_context = self.jaeger.create_context(span)
                self.kafka.push(constants.kafka.MODEL_DISPATCH, trace_context)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
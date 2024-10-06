from funcs import kafka_utils, jaeger_utils
from funcs import thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('data_refinery')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DATA_REFINERY, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        with self.jaeger.create_span('SANITIZING STOCK DATA') as parent:
            misc.timeout_range(0.03, 0.08)

            def first():
                with self.jaeger.create_span('WROTE INFERENCE DATA TO KAFKA', parent) as span:
                    misc.timeout_range(0.1, 0.15)

                    trace_context = self.jaeger.create_context(span)
                    self.kafka.push(constants.kafka.MODEL_DISPATCH, trace_context)

            def second():
                with self.jaeger.create_span('WROTE SANITIZED STOCK DATA TO DB', parent) as span:
                    misc.timeout_range(0.20, 0.30)

            thread_utils.start_thread(first)
            thread_utils.start_thread(second)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
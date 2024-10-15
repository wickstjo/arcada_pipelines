from common import kafka_utils, cassandra_utils, jaeger_utils, thread_utils, misc, constants

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.cassandra = cassandra_utils.create_instance()
        self.kafka = kafka_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('DRIFT_ANALYSIS')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.DRIFT_ANALYSIS, self.on_kafka_event, structs.thread_beacon)

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_input: dict):
        assert 'trace' in kafka_input, "[DRIFT] EVENT MISSING 'trace' PROPERTY"
        assert 'models_used' in kafka_input, "[DRIFT] EVENT MISSING 'models_used' PROPERTY"
        trace_predecessor = kafka_input['trace']

        for model_props in kafka_input['models_used']:
            thread_utils.start_thread(self.measure_model_drift, (
                model_props,
                trace_predecessor
            ))

    # IN SEPARATE THREADS -- MEASURE DRIFT OF MODELS THAT WERE USED DURING INFERENCE
    def measure_model_drift(self, model_props, trace_predecessor):
        assert 'model_name' in model_props, "[DRIFT] MODEL MISSING 'model_name' PROPERTY"
        assert 'model_version' in model_props, "[DRIFT] MODEL MISSING 'model_version' PROPERTY"

        model_name = model_props['model_name']
        model_version = model_props['model_version']

        with self.jaeger.create_span(f"MEASURING DRIFT OF '{model_name} v{model_version}'", trace_predecessor) as span:
            misc.timeout_range(0.02, 0.04)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
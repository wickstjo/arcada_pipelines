from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import funcs.constants as constants
import machine_learning.options as ml_options
import funcs.types as types

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_ANALYSIS

        # WHAT MODELS DO WE CURRENTLY ACCEPT
        # HOW DO WE LOAD THE MODELS, AND HOW DO WE USE THEM?
        self.model_options: dict = ml_options.IMPLEMENTED_MODELS()

        ### TODO: PRELOAD ALL MODEL PROBES
        ### TODO: PRELOAD ALL MODEL PROBES
        ### TODO: PRELOAD ALL MODEL PROBES
        self.model_probes = ml_options.IMPLEMENTED_PROBES()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # VALIDATE THE REQUEST INPUTS
        target_model = misc.validate_dict(kafka_input, types.ANALYSIS_REQUEST, ns=True)

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        if target_model.model_type not in self.model_options:
            raise Exception(f'ERROR: CANNOT PROCESS MODELS OF TYPE ({target_model.model_type})')

        # INSTANTIATE THE CORRECT MODEL SUITE & LOAD A MODEL FROM FILE
        model_suite = self.model_options[target_model.model_type]()
        model = model_suite.load_model(target_model.model_filename)

        # START PROBING THE MODEL
        for probe in self.model_probes:
            defect_found: bool = probe.apply(model)

            # WHEN A DEFECT/LARGE DRIFT IS FOUND, TRIGGER MODEL RETRAINING
            # TODO: ONLY ONE MATCH IS REQUIRED, MAYBE CHANGE THIS TO BE A RANGE OR MAJORITY VOTE?
            if defect_found:
                self.request_retraining(target_model)
                return
        
        # OTHERWISE, THE MODEL SEEMS TO WORK FINE
        misc.log('PROBING COMPLETE: MODEL DOES NOT NEED TO BE RE-TRAINED')


########################################################################################
########################################################################################

    def request_retraining(self, model_predecessor: dict):

        # WRITE & VALIDATE A MODEL TRAINING REQUEST
        training_request: dict = misc.validate_dict({
            'predecessor': model_predecessor.uuid,
            'model_type': model_predecessor.model_type,
            'model_name': model_predecessor.name,
            'model_version': model_predecessor.version + 1,
        }, types.TRAINING_REQUEST)

        # PUSH RE-TRAINING REQUEST TO KAFKA
        self.kafka_producer.push_msg(constants.kafka.MODEL_TRAINING, training_request)

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc

# import funcs.ml_utils as ml_utils
import funcs.machine_learning.utils as ml_utils

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = 'model_analysis'
        self.model_training_topic: str = 'model_training'

        ################################# TODO: FIX THIS
        ################################# TODO: FIX THIS
        ################################# TODO: FIX THIS
        self.model_params_type: dict = {
            'model_type': str,
            'model_filename': str,
        }

        # WHAT MODELS DO WE CURRENTLY ACCEPT
        # HOW DO WE LOAD THE MODELS, AND HOW DO WE USE THEM?
        self.model_options: dict = ml_utils.IMPLEMENTED_MODELS()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # VALIDATE THE REQUEST INPUTS
        request = misc.validate_dict(kafka_input, self.model_params_type)
        model_type = request['model_type']
        model_filename = request['model_filename']

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        if model_type not in self.model_options:
            raise Exception(f'ERROR: CANNOT PROCESS MODELS OF TYPE ({model_type})')

        # INSTANTIATE THE CORRECT MODEL SUITE & LOAD A MODEL FROM FILE
        # THEN PERFORM AN ANALYSIS TO DETERMINE WHETHER A NEW MODEL SHOULD BE TRAINED
        model_suite = self.model_options[model_type]()
        re_train_decision = model_suite.analysis(model_filename)

        # WHEN ANALYSIS RETURNS TRUE, TRIGGER MODEL RE-TRAIN
        if re_train_decision:
            self.kafka_producer.push_msg(self.model_training_topic, {

                ################################# TODO: FIX THIS
                ################################# TODO: FIX THIS
                ################################# TODO: FIX THIS
                'model_name': str,
                'model_type': 'MISSING_RETRAIN_TYPE',
                'dataset_rows': 696969
            })

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
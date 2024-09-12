from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import funcs.constants as constants

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
        self.model_options: dict = constants.IMPLEMENTED_MODELS()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # VALIDATE THE REQUEST INPUTS
        model_info = misc.validate_dict(kafka_input, constants.types.MODEL_INFO)
        model_type = model_info['model_type']
        model_filename = model_info['model_filename']

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        if model_type not in self.model_options:
            raise Exception(f'ERROR: CANNOT PROCESS MODELS OF TYPE ({model_type})')

        # INSTANTIATE THE CORRECT MODEL SUITE & LOAD A MODEL FROM FILE
        # THEN PERFORM AN ANALYSIS TO DETERMINE WHETHER A NEW MODEL SHOULD BE TRAINED
        model_suite = self.model_options[model_type]()
        re_train_decision = model_suite.analysis(model_filename)

        # THE MODEL DOES NOT YET NEED TO BE RE-TRAINED
        if not re_train_decision:
            misc.log('ANALYSIS: MODEL DOES NOT NEED TO BE RE-TRAINED')
            pass

        # OTHERWISE, WRITE & VALIDATE A MODEL TRAINING REQUEST
        valid_training_request: dict = misc.validate_dict({

            ################################# TODO: FIX THIS
            ################################# TODO: FIX THIS
            ################################# TODO: FIX THIS
            'model_name': str,
            'model_type': 'MISSING_RETRAIN_TYPE',
            'dataset_rows': 696969,

        }, constants.types.MODEL_TRAINING_REQUEST)

        # PUSH RE-TRAINING REQUEST TO KAFKA
        self.kafka_producer.push_msg(constants.kafka.MODEL_TRAINING, valid_training_request)

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
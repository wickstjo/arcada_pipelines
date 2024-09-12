from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.constants as constants
import funcs.misc as misc
import funcs.thread_utils as thread_utils

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
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_INFERENCE

        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = constants.IMPLEMENTED_MODELS()

        # CURRENTLY LOADED MODELS
        self.model_mutex = thread_utils.create_mutex()
        self.loaded_models: dict = {}

        # EVERY N SECONDS, CHECK CASSANDRA FOR MODEL CHANGES
        thread_utils.background_process(self.audit_model_status, 2, process_beacon)

    ########################################################################################
    ########################################################################################

    def audit_model_status(self):
    
        # CHECK DB FOR WHAT MODELS SHOULD CURRENTLY BE ACTIVE
        query_result: list[dict] = self.cassandra.read(
            f"SELECT * FROM {constants.cassandra.MODELS_TABLE} WHERE active_status = True ALLOW FILTERING"
        )

        print(query_result)
        return

        # LOOP THROUGH MODELS
        for item in query_result:

            # MODEL CANT BE FOUND IN STATE, THEREFORE ADD IT
            if item['model_name'] not in self.loaded_models:
                with self.model_mutex:
                    self.deploy_model(item)
                    misc.log('DEPLOYED NEW MODEL')
                continue

            # OTHERWISE, THE MODEL IS LOADED
            # IF THERE IS A NEWER VERSION OF THIS MODEL AVAILABLE
            if item['version'] > self.loaded_models['model_name'].version:
                with self.model_mutex:

                    # RETIRE THE OLD MODEL & DEPLOY THE NEW ONE
                    del self.loaded_models['model_name']
                    self.deploy_model(item)
                    misc.log('RETRIED OLD MODEL AND DEPLOYED NEW MODEL')
        
    ########################################################################################
    ########################################################################################

    def deploy_model(self, model_info: dict):

        # VALIDATE THE REQUEST INPUTS
        model_type = model_info['model_type']
        model_filename = model_info['model_filename']

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        if model_type not in self.model_options:
            raise Exception(f'ERROR: CANNOT PROCESS MODELS OF TYPE ({model_type})')

        # MAKE SURE WE DONT DOUBLE-LOAD THE SAME MODEL
        if model_filename in self.loaded_models:
            raise Exception(f'ERROR: MODEL ALREADY LOADED ({model_filename})')

        # INSTANTIATE THE CORRECT MODEL SUITE & LOAD A MODEL FROM FILE
        model_suite = self.model_options[model_type]()
        model_suite.load_model(model_filename)

        # SAVE THE MODEL SUITE IN STATE FOR REPEATED USE
        self.loaded_models[model_filename] = model_suite

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE INPUT IS PROPER STOCK DATA
        refined_stock_data: dict = misc.validate_dict(kafka_input, constants.types.REFINED_STOCK_DATA)

        # DISABLE INFERENCE WHEN NO MODELS HAVE BEEN LOADED
        if len(self.loaded_models) == 0:
            misc.log('PAUSED: NO DEPLOYED MODELS YET')
            return

        # GENERATE A PREDICTION FOR EACH LOADED MODEL
        model_predictions: dict = self.query_all_models(refined_stock_data)
        misc.log(f'GENERATED {len(model_predictions)} PREDICTIONS')

        ### TODO: VALIDATE INPUT FIRST
        ### TODO: VALIDATE INPUT FIRST
        ### TODO: VALIDATE INPUT FIRST

        # PUSH THE INPUT ROW & ALL PREDICTIONS TO THE DECISION SYNTHESIS MODULE
        self.kafka_producer.push_msg(constants.kafka.DECISION_SYNTHESIS, {
            'input_row': refined_stock_data,
            'predictions': model_predictions
        })

    ########################################################################################
    ########################################################################################

    def query_all_models(self, model_input: dict) -> dict:
        predictions = {}
        
        # FEED THE INPUT TO EACH MODELS RESPECTIVE USE FUNC
        with self.model_mutex:
            for model_name, model_suite in self.loaded_models.items():
                predictions[model_name] = model_suite.predict_outcome(model_input)

        return predictions

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
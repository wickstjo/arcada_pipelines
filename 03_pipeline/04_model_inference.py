from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
from funcs.redis_utils import create_redis_instance
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
        self.redis = create_redis_instance(process_beacon)

        # SUBSCRIBE TO PIPELINE EVENTS VIA REDIS
        redis_channels: str|list[str] = 'events.model_trained'
        self.redis.subscribe(redis_channels, self.on_redis_event)

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = 'model_inference'
        self.decision_synthesis_topic: str = 'decision_synthesis'

        # WHEN A NEW MODEL HAS BEEN TRAINED, WHAT SHOULD THE HANDSHAKE LOOK LIKE?
        self.new_model_type: dict = {
            'model_type': str,
            'model_filename': str,
        }

        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = ml_utils.IMPLEMENTED_MODELS()

        # CURRENTLY LOADED MODELS
        self.loaded_models: dict = {}

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # DISABLE INFERENCE WHEN NO MODELS HAVE BEEN LOADED
        if len(self.loaded_models) == 0:
            raise Exception('ERROR: NO DEPLOYED MODELS YET')

        # GENERATE A PREDICTION FOR EACH LOADED MODEL
        predictions: dict = self.query_all_models(kafka_input)
        misc.log(f'GENERATED {len(predictions)} PREDICTIONS')

        # PUSH THE INPUT ROW & ALL PREDICTIONS TO THE DECISION SYNTHESIS MODULE
        self.kafka_producer.push_msg(self.decision_synthesis_topic, {
            'input_row': kafka_input,
            'predictions': predictions
        })

    ########################################################################################
    ########################################################################################

    def query_all_models(self, model_input: dict) -> dict:
        predictions = {}
        
        # FEED THE INPUT TO EACH MODELS RESPECTIVE USE FUNC
        for model_name, model_suite in self.loaded_models.items():
            predictions[model_name] = model_suite.predict_outcome(model_input)

        return predictions

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING REDIS CACHE EVENTS
    def on_redis_event(self, redis_channel: str, redis_input: dict):
        misc.log('A NEW MODEL HAS BEEN TRAINED')
        print(redis_input)
        # self.deploy_model

    ########################################################################################
    ########################################################################################

    def deploy_model(self, kafka_input: dict):

        # VALIDATE THE REQUEST INPUTS
        request = misc.validate_dict(kafka_input, self.new_model_type)
        model_type = request['model_type']
        model_filename = request['model_filename']

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


        ### CHANGE THIS TO REDIS
        ### CHANGE THIS TO REDIS
        ### CHANGE THIS TO REDIS

        # # START ACCEPTING INPUT DATA FOR MODEL
        # self.kafka_producer.push_msg(self.output_topic, {
        #     'model_topic_name': 'START_FLOODING_DATA_HERE'
        # })


########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
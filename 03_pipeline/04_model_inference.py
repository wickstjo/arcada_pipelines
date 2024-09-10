from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.input_topics: list[str] = ['model_inference', 'events.model_trained']
        self.output_topic: str = 'events.model_deployed'

        # WHEN A NEW MODEL HAS BEEN TRAINED, WHAT SHOULD THE HANDSHAKE LOOK LIKE?
        self.new_model_type: dict = {
            'model_name': str,
            'model_type': str,
            'model_filename': str,
        }

        # WHAT MODELS DO WE CURRENTLY ACCEPT
        # HOW DO WE LOAD THE MODELS, AND HOW DO WE USE THEM?
        self.model_options = {
            'lstm': [self.load_lstm, self.use_lstm],
            'cnn': [self.load_cnn, self.use_cnn],
            'linreg': [self.load_linreg, self.use_linreg],
        }

        # CURRENTLY LOADED MODELS
        self.loaded_models = {}

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def handle_event(self, kafka_topic: str, kafka_input: dict):

        # USE A CURRENTLY DEPLOYED MODEL
        if kafka_topic == 'model_inference':
            self.use_model(kafka_input)

        # DEPLOY A NEW MODEL
        if kafka_topic == 'events.model_trained':
            self.deploy_model(kafka_input)

    ########################################################################################
    ########################################################################################

    def deploy_model(self, kafka_input: dict):

        # VALIDATE THE REQUEST INPUTS
        request = misc.validate_dict(kafka_input, self.new_model_type)
        model_type = request['model_type']
        model_filename = request['model_filename']
        model_name = request['model_name']

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        if model_type not in self.model_options:
            raise Exception(f'ERROR: CANNOT PROCESS MODELS OF TYPE ({model_type})')

        # MAKE SURE MODEL NAME IS UNIQUE
        if model_name in self.loaded_models:
            raise Exception(f'ERROR: MODEL NAME ALREADY EXISTS ({model_name})')

        # OTHERWISE EXTRACT THE MODEL TYPE COMPONENTS
        load_model_func, use_model_func = self.model_options[model_type]

        # LOAD THE MODEL & SAVE THE MODEL IN STATE
        model = load_model_func(model_filename)
        self.loaded_models[model_name] = [use_model_func, model]

        # START ACCEPTING INPUT DATA FOR MODEL
        self.kafka_producer.push_msg(self.output_topic, {
            'model_topic_name': 'START_FLOODING_DATA_HERE'
        })

    ########################################################################################
    ########################################################################################

    def use_model(self, model_input: dict):

        # DISABLE INFERENCE WHEN NO MODELS HAVE BEEN LOADED
        if len(self.loaded_models) == 0:
            raise Exception('NO MODELS LOADED, CANNOT INFER YET')
        
        # FEED THE INPUT TO EACH MODELS RESPECTIVE USE FUNC
        for item in self.loaded_models.values():
            use_func, model = item
            use_func(model, model_input)

    ########################################################################################
    ########################################################################################

    def load_lstm(self, file_name):
        misc.log(f'LOADED LSTM MODEL ({file_name})')
        return True

    def use_lstm(self, model, model_input: dict):
        misc.log(f'PREDICTED WITH LSTM MODEL')
        pass

    ########################################################################################
    ########################################################################################

    def load_cnn(self, file_name):
        misc.log(f'LOADED CNN MODEL ({file_name})')
        return True

    def use_cnn(self, model, model_input: dict):
        misc.log(f'PREDICTED WITH CNN MODEL')
        pass

    ########################################################################################
    ########################################################################################

    def load_linreg(self, file_name):
        misc.log(f'LOADED LINEAR REGRESSION MODEL ({file_name})')
        return True

    def use_linreg(self, model, model_input: dict):
        misc.log(f'PREDICTED WITH LINREG MODEL')
        pass

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
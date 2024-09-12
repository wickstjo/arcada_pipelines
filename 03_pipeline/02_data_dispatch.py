from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
import funcs.misc as misc

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT 
        self.kafka_producer = create_kafka_producer()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = 'data_dispatch'
        self.model_training_topic: str = 'model_training'
        self.model_inference_topic: str = 'model_inference'

        # WHEN A NEW MODEL IS ADDED, WHAT SHOULD THE HANDSHAKE MESSAGE CONTAIN?
        self.model_deployed_type: dict = {
            'model_topic_name': str,
        }

        # TRACK WHAT TOPICS ARE READY TO RECEIVE DATA
        self.awaiting_topics: list[str] = []

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # WHEN A NEW MODEL IS TRAINED & DEPLOYED -- ADD IT TO THE STATE
        if kafka_topic == 'events.model_deployed':
            self.add_model(kafka_input)
        
        # OTHERWISE, ITS A DATA DISPATCHING EVENT
        # FORWARD DATA TO AWAITING MODEL TOPICS
        if kafka_topic == 'data_dispatch':
            self.forward_data(kafka_input)

    ########################################################################################
    ########################################################################################

    # A NEW MODEL HAS BEEN CREATED, ADD IT TO THE LIST
    def add_model(self, kafka_input: dict):
        valid_input = misc.validate_dict(kafka_input, self.model_deployed_type)
        new_topic = valid_input['model_topic_name']
        self.awaiting_topics.append(new_topic)
        misc.log('MODEL ADDED TO STATE')

    ########################################################################################
    ########################################################################################

    # FORWARD DATA TO AWAITING MODEL TOPICS
    def forward_data(self, kafka_input: dict):
        for target_topic in self.awaiting_topics:
            self.kafka_producer.push_msg(target_topic, kafka_input)
        misc.log('FORWARDED DATA TO ALL MODELS')

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
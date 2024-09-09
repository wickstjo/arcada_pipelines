import utils.kafka_utils as kafka_utils
import utils.misc as misc

########################################################################################
########################################################################################

class create_state:
    def __init__(self):

        # RELEVANT KAFKA TOPICS
        self.input_topics: list[str] = ['data_dispatch', 'events.model_deployed']
        self.model_training_topic: str = 'model_training'
        self.model_inference_topic: str = 'model_inference'

        # REFERENCE FOR WHAT THE 'events.model_deployed' EVENT SHOULD CONTAIN
        self.ref_model_deployed = {
            'model_topic_name': str,
        }
    
        # TRACK WHAT TOPICS ARE READY TO RECEIVE DATA
        self.awaiting_topics: list[str] = []
    
    # A NEW MODEL HAS BEEN CREATED, ADD IT TO THE LIST
    def add_model(self, kafka_input):
        valid_input = misc.validate_dict(kafka_input, self.ref_model_deployed)
        new_topic = valid_input['model_topic_name']
        self.awaiting_topics.append(new_topic)
        misc.log('MODEL ADDED TO STATE')

    # FORWARD DATA TO AWAITING MODEL TOPICS
    def forward_data(self, kafka_input, kafka_producer):
        for target_topic in self.awaiting_topics:
            kafka_producer.push_msg(target_topic, kafka_input)
        misc.log('FORWARDED DATA TO ALL MODELS')

state = create_state()

########################################################################################
########################################################################################

def handle_event(kafka_topic: str, kafka_input: dict, support_structs: list):

    # EXTRACT THE SUPPORT STRUCTS -- ORDER: (KAFKA_PRODUCER, CASSANDRA, GLOBAL_CONFIG)
    kafka_producer = support_structs[0]

    # WHEN A NEW MODEL IS TRAINED & DEPLOYED -- ADD IT TO THE STATE
    if kafka_topic == 'events.model_deployed':
        state.add_model(kafka_input)
    
    # OTHERWISE, ITS A DATA DISPATCHING EVENT
    # FORWARD DATA TO AWAITING MODEL TOPICS
    if kafka_topic == 'data_dispatch':
        state.forward_data(kafka_input, kafka_producer)

########################################################################################
########################################################################################

kafka_utils.start_flex_consumer(
    state.input_topics,
    handle_event,

    # DOES YOUR FUNCTION NEED A KAFKA PRODUCER, CASSANDRA CLIENT OR THE GLOBAL CONFIG?
    # REMEMBER TO ADD/REMOVE THEM AS INPUT ARGS TO handle_events ^
    # KEEP THIS ORDER!
    include_kafka_producer=True,
    # include_cassandra=True,
    # include_config=True,
)
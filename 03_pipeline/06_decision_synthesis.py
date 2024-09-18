from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import funcs.constants as constants
import funcs.types as types

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = constants.kafka.DECISION_SYNTHESIS

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE KAFKA INPUT IS VALID
        prediction_batch = misc.validate_dict(kafka_input, types.PREDICTION_BATCH)

        # MAKE DECISION
        misc.log('NEW BATCH OF PREDICTION RECEIVED')

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
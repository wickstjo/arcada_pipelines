from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = 'decision_synthesis'

        # WHAT FORMAT SHOULD KAFKA INPUT FOLLOW?
        self.expected_input_format: dict = {
            'input_row': str,
            'predictions': dict
        }

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE KAFKA INPUT IS VALID
        valid_input = misc.validate_dict(kafka_input, self.expected_input_format)

        # MAKE DECISION
        print(valid_input)

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
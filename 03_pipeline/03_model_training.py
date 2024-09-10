from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.misc as misc
import time

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT 
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.input_topics: str = 'model_training'
        self.output_topic: str = 'events.model_trained'

        # THE CASSANDRA TABLE WITH REFINED DATA
        self.cassandra_table: str = 'refined.stock_data'

        # WHAT SHOULD A MODEL TRAINING REQUEST CONTAIN?
        self.model_training_request_type: dict = {
            'model_name': str,
            'model_type': lambda x: str(x).lower(),
            'dataset_rows': int,
        }

        # WHAT MODELS CAN WE CURRENTLY TRAIN?
        self.model_options = {
            'linreg': self.train_linreg,
            'lstm': self.train_lstm,
            'cnn': self.train_cnn,
        }

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def handle_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        request = misc.validate_dict(kafka_input, self.model_training_request_type)
        model_type = request['model_type']

        # THROW ERROR IF THE REQUESTED MODEL TYPE IS NOT AVAILABLE
        if model_type not in self.model_options.keys():
            raise Exception(f'MODEL TYPE NOT AVAILABLE ({model_type})')

        # OTHERWISE, START TRAINING ONE
        misc.log(f'MODEL TRAINING STARTED ({model_type})')
        self.model_options[model_type](request)
        misc.log(f'MODEL TRAINING FINISHED ({model_type})')

        # NOTIFY THE MODEL INFERENCE PROCESS THAT A NEW MODEL IS AVAILABLE
        self.kafka_producer.push_msg(self.output_topic, {
            'model_name': request['model_name'],
            'model_type': request['model_type'],
        })

    ########################################################################################
    ########################################################################################

    # ATTEMPT TO FETCH A N-SIZED DATASET
    # IF THERE ARENT ENOUGH ROWS YET, WAIT UNTIL THERE IS..
    def fetch_dataset(self, minimum_num_rows: int):
        
        # QUERY HOW MANY ROWS THE DATABASE HAS RIGHT NOW
        current_num_rows = self.cassandra.count_rows(self.cassandra_table)

        # IF THERE ARENT ENOUGH ROWS YET..
        # SLEEP FOR ABIT WHILE THE DATABASE FILLS UP
        while current_num_rows < minimum_num_rows:
            misc.log(f'NOT ENOUGH DB ROWS ({current_num_rows}/{minimum_num_rows}), WAITING..')
            time.sleep(5)

            # QUERY AGAIN
            current_num_rows = self.cassandra.count_rows(self.cassandra_table)

        # MIN ROW COUNT EXCEEDED, FETCH THE DATASET
        misc.log(f'FETCHING DATASET (n={minimum_num_rows})')
        return []

    ########################################################################################
    ########################################################################################

    def train_linreg(self, request: dict):

        # FETCH FRESH DATA FROM DB
        dataset = self.fetch_dataset(request['dataset_rows'])

    ########################################################################################
    ########################################################################################

    def train_lstm(self, request: dict):

        # FETCH FRESH DATA FROM DB
        dataset = self.fetch_dataset(request['dataset_rows'])

    ########################################################################################
    ########################################################################################

    def train_cnn(self, request: dict):
        
        # FETCH FRESH DATA FROM DB
        dataset = self.fetch_dataset(request['dataset_rows'])

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
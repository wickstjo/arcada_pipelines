from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
from funcs.redis_utils import create_redis_instance
import funcs.misc as misc
import time

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

        # RELEVANT KAFKA TOPICS
        self.input_topics: str|list[str] = 'model_training'
        self.output_topic: str = 'events.model_trained'

        # THE CASSANDRA TABLE WITH REFINED DATA
        self.cassandra_table: str = 'refined.stock_data'

        # WHAT SHOULD A MODEL TRAINING REQUEST CONTAIN?
        self.model_training_request_type: dict = {
            'model_name': str,
            'model_type': lambda x: str(x).lower(),
            'dataset_rows': int,
        }

        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = ml_utils.IMPLEMENTED_MODELS()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        request = misc.validate_dict(kafka_input, self.model_training_request_type)
        model_type = request['model_type']
        model_name = request['model_name']

        # THROW ERROR IF THE REQUESTED MODEL TYPE IS NOT AVAILABLE
        if model_type not in self.model_options.keys():
            raise Exception(f'MODEL TYPE NOT AVAILABLE ({model_type})')

        # ATTEMPT TO LOAD DATASET -- BLOCKING UNTIL DATABASE HAS ENOUGH ROWS
        dataset = self.fetch_dataset(request['dataset_rows'])

        # MEASURE STARTING TIME
        misc.log(f'MODEL TRAINING STARTED ({model_type})..')
        training_started: float = time.time()

        # STITCH TOGETHER A MODEL ID
        now = int(time.time())
        model_id = f'{now}_{model_type}_{model_name}'

        # INSTANTATE THE A MODEL SUITE & START TRAINING 
        model_suite = self.model_options[model_type]()
        model_suite.train_model(dataset, model_id)

        # MEASURE DELTA TIME
        training_ended: float = time.time()
        delta_time: float = round(training_ended - training_started, 2)
        misc.log(f'MODEL TRAINING FINISHED ({model_type}) IN {delta_time} SECONDS')






        ### CHANGE THIS TO REDIS
        ### CHANGE THIS TO REDIS
        ### CHANGE THIS TO REDIS

        # # NOTIFY THE MODEL INFERENCE PROCESS THAT A NEW MODEL IS AVAILABLE
        # self.kafka_producer.push_msg(self.output_topic, {
        #     'model_name': request['model_name'],
        #     'model_type': request['model_type'],
        # })

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

start_kafka_consumer(create_pipeline_component)
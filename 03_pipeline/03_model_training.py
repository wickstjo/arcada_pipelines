from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.constants as constants
import funcs.types as types
import machine_learning.options as ml_options
import funcs.misc as misc
import time

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT 
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # WHAT KAFKA TOPIC DO YOU WANT TO CONSUME DATA FROM?
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_TRAINING
        
        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = ml_options.IMPLEMENTED_MODELS()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        training_request = misc.validate_dict(kafka_input, types.TRAINING_REQUEST, ns=True)

        # THROW ERROR IF THE REQUESTED MODEL TYPE IS NOT AVAILABLE
        if training_request.model_type not in self.model_options.keys():
            raise Exception(f'[MAIN] MODEL TYPE NOT AVAILABLE ({training_request.model_type})')
        
        # STITCH TOGETHER A UNIQUE FILENAME FOR THE MODEL
        model_filename: str = f'{training_request.model_type}::{training_request.model_name}::v{training_request.model_version}'
        
        # CHECK DB IF A MODEL WITH THESE PARAMS ALREADY EXISTS
        count_query: str = f"SELECT COUNT(*) FROM {constants.cassandra.MODELS_TABLE} WHERE model_filename = '{model_filename}' ALLOW FILTERING"
        db_matches: int = self.cassandra.count(count_query)

        # IF IT DOES, TERMINATE..
        if db_matches > 0:
            raise Exception('A MODEL WITH THESE EXACT PARAMS ALREADY EXISTS')
        
        # OTHERWISE, CREATE THE REQUESTED MODEL SUITE
        # ATTEMPT TO LOAD ITS DATASET -- BLOCKING UNTIL DATABASE HAS ENOUGH ROWS
        model_suite = self.model_options[training_request.model_type]()
        dataset = self.fetch_dataset(model_suite.required_dataset_size)

        misc.log(f'[MAIN] MODEL TRAINING STARTED ({training_request.model_type})..')
        training_timer = misc.create_timer()

        # INSTANTATE THE A MODEL SUITE & START TRAINING 
        model_suite = self.model_options[training_request.model_type]()
        model_suite.train_model(dataset, model_filename)

        delta_time: float = training_timer.stop()
        misc.log(f'[MAIN] MODEL TRAINING FINISHED IN {delta_time} SECONDS')

        # IF THE MODEL HAD A PREDECESSOR, RETIRE IT
        if training_request.predecessor:
            self.cassandra.query(f"UPDATE {constants.cassandra.MODELS_TABLE} SET active_status = False WHERE uuid = {training_request.predecessor}")
            misc.log('[MAIN] RETIRED MODEL PREDECESSOR')

        # CONSTRUCT & VALIDATE NEW MODEL OBJECT
        new_model: dict = misc.validate_dict({
            'uuid': misc.create_uuid(),
            'timestamp': int(training_timer.end_time),
            'model_name': training_request.model_name,
            'model_type': training_request.model_type,
            'model_version': training_request.model_version,
            'model_file': model_filename,
            'active_status': True,
        }, types.MODEL_INFO)

        # THEN PUSH IT TO KAFKA
        self.cassandra.write(constants.cassandra.MODELS_TABLE, new_model)
        misc.log('[MAIN] UPLOADED NEW MODEL')

    ########################################################################################
    ########################################################################################

    # ATTEMPT TO FETCH A N-SIZED DATASET
    # IF THERE ARENT ENOUGH ROWS YET, WAIT UNTIL THERE IS..
    def fetch_dataset(self, minimum_num_rows: int):
        
        # QUERY HOW MANY ROWS THE DATABASE HAS RIGHT NOW
        current_num_rows: int = self.cassandra.count(f'SELECT COUNT(*) FROM {constants.cassandra.STOCKS_TABLE}')

        # IF THERE ARENT ENOUGH ROWS YET..
        # SLEEP FOR ABIT WHILE THE DATABASE FILLS UP
        while current_num_rows < minimum_num_rows:
            misc.log(f'[MAIN] NOT ENOUGH DB ROWS ({current_num_rows}/{minimum_num_rows}), WAITING..')
            time.sleep(5)

            # QUERY AGAIN
            current_num_rows = self.cassandra.count(f'SELECT COUNT(*) FROM {constants.cassandra.STOCKS_TABLE}')

        # MIN ROW COUNT EXCEEDED, FETCH THE DATASET
        misc.log(f'[MAIN] FETCHING DATASET (n={minimum_num_rows})')
        return []

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
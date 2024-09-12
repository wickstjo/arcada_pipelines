from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
from funcs.redis_utils import create_redis_instance
import funcs.constants as constants
import funcs.misc as misc
import time

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT 
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()
        self.redis = create_redis_instance(process_beacon)

        # WHAT KAFKA TOPIC DO YOU WANT TO CONSUME DATA FROM?
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_TRAINING
        
        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = constants.IMPLEMENTED_MODELS()

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        training_request = misc.validate_dict(kafka_input, constants.types.MODEL_TRAINING_REQUEST)
        model_name = training_request['model_name']
        model_type = training_request['model_type']
        model_version = training_request['model_version']

        ### TODO: ADD MODEL VERSIONING
        ### TODO: ADD MODEL VERSIONING
        ### TODO: ADD MODEL VERSIONING

        # THROW ERROR IF THE REQUESTED MODEL TYPE IS NOT AVAILABLE
        if model_type not in self.model_options.keys():
            raise Exception(f'MODEL TYPE NOT AVAILABLE ({model_type})')

        # ATTEMPT TO LOAD DATASET -- BLOCKING UNTIL DATABASE HAS ENOUGH ROWS
        dataset = self.fetch_dataset(training_request['dataset_rows'])

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
        delta_time: float = round(training_ended - training_started, 3)
        misc.log(f'MODEL TRAINING FINISHED ({model_type}) IN {delta_time} SECONDS')

        ### TODO: CONDITIONALLY, RETIRE THE OLD MODEL VERSION IN DB
        ### TODO: CONDITIONALLY, RETIRE THE OLD MODEL VERSION IN DB
        ### TODO: CONDITIONALLY, RETIRE THE OLD MODEL VERSION IN DB

        # self.cassandra.query(f"UPDATE {constants.CASSANDRA_MODELS_TABLE} SET active_status = False WHERE model_name = {}")

        # PUSH MODEL REFERENCE TO CASSANDRA
        self.cassandra.write(constants.cassandra.MODELS_TABLE, {
            'timestamp': int(training_ended),
            'model_name': model_id,
            'model_type': model_type,
            'model_version': model_version+1,
            'active_status': True,
        })

    ########################################################################################
    ########################################################################################

    # ATTEMPT TO FETCH A N-SIZED DATASET
    # IF THERE ARENT ENOUGH ROWS YET, WAIT UNTIL THERE IS..
    def fetch_dataset(self, minimum_num_rows: int):
        
        # QUERY HOW MANY ROWS THE DATABASE HAS RIGHT NOW
        current_num_rows = self.cassandra.count_rows(constants.cassandra.STOCKS_TABLE)

        # IF THERE ARENT ENOUGH ROWS YET..
        # SLEEP FOR ABIT WHILE THE DATABASE FILLS UP
        while current_num_rows < minimum_num_rows:
            misc.log(f'NOT ENOUGH DB ROWS ({current_num_rows}/{minimum_num_rows}), WAITING..')
            time.sleep(5)

            # QUERY AGAIN
            current_num_rows = self.cassandra.count_rows(constants.cassandra.STOCKS_TABLE)

        # MIN ROW COUNT EXCEEDED, FETCH THE DATASET
        misc.log(f'FETCHING DATASET (n={minimum_num_rows})')
        return []

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
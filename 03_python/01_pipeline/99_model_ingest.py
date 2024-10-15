from common import kafka_utils, thread_utils, constants
from .funcs import dataset_utils
import time

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # USE QUEUES?

        # LOAD DATASET FROM DB
        # VERIFY ORDER
        # CREATE QUEUE
        # RECURSIVELY PUSH MOVING WINDOW INTO QUEUE 

        # SPAWN N THREADS
        # LOAD N MODELS
            # DEQUEUE ITEMS FROM QUEUE
            # RUN THROUGH MODEL
            # WRITE PREDICTION TO DB
        
        {
            'input_tbl': 'john.refined_stock_data',
            'input_rows': [1234, 5678],
            'model_name': 'foo',
            'model_version': 12,
            'prediction': {
                'value': 'foo'
            }
        }


        ### MODEL PREDICTIONS TABLE
        {
            'timestamp': str,
            'model_name': str,
            'model_version': int,
            'input': {
                'value': any
            },
            'prediction': {
                'value': any
            },
        }




        # CREATE INSTANCED CLIENTS
        kafka = kafka_utils.create_instance()

        # LOAD IN THE STREAMING DATASET
        dataset_path: str = structs.global_config.pipeline.data_ingestion.gradual.dataset
        dataset = dataset_utils.load_csv(dataset_path)

        # PUSH THE ROWS INTO KAFKA
        # NOTE THAT ALL VALUES ARE STRINGIFIED ON-PURPOSE
        # TO NOT CHEAT AND SKIP PRE-PROCESSING
        for unprocessed_row in dataset:
            kafka.push(constants.kafka.DATA_REFINERY, unprocessed_row)

            # SLEEP FOR ABIT TO SIMULATE THE REAL WORLD
            time.sleep(structs.global_config.pipeline.data_ingestion.gradual.delay)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component, poll=False)
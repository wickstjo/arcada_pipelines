from funcs import kafka_utils
from funcs import thread_utils, misc, constants
import time

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        kafka = kafka_utils.create_instance()

        # LOAD IN THE STREAMING DATASET
        dataset_path: str = structs.global_config.pipeline.data_ingestion.datasets.streaming
        dataset = misc.load_csv(dataset_path)

        # PUSH THE ROWS INTO KAFKA
        # NOTE THAT ALL VALUES ARE STRINGIFIED ON-PURPOSE
        # TO NOT CHEAT AND SKIP PRE-PROCESSING
        for unprocessed_row in dataset:
            kafka.push(constants.kafka.DATA_REFINERY, unprocessed_row)

            # SLEEP FOR ABIT TO SIMULATE THE REAL WORLD
            time.sleep(structs.global_config.pipeline.data_ingestion.streaming_delay)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component, poll=False)
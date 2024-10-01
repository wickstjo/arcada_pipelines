from funcs import kafka_utils
from funcs import thread_utils, misc, constants
import time

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, thread_beacon):

        # CREATE INSTANCED CLIENTS
        kafka = kafka_utils.create_instance()

        # LOAD THE DATASET
        source_dataset: str = 'datasets/finance_fresh.csv'
        dataset = misc.load_csv(source_dataset)

        # DELAY INJECTIONS TO SIMULATE REAL WORLD
        injection_cooldown: float = 1.0

        # PUSH THE ROWS INTO KAFKA
        # NOTE THAT ALL VALUES ARE STRINGIFIED ON-PURPOSE
        # TO NOT CHEAT AND SKIP PRE-PROCESSING
        for unprocessed_row in dataset:
            kafka.push(constants.kafka.DATA_REFINERY, unprocessed_row)
            time.sleep(injection_cooldown)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component, poll=False)
from funcs.kafka_utils import create_kafka_producer
import funcs.misc as misc
import funcs.constants as constants
import time
from dataclasses import dataclass

########################################################################################
########################################################################################

@dataclass(frozen=True)
class state:
    dataset_file: str = 'datasets/finance_fresh.csv'
    injection_cooldown: float = 1.0

########################################################################################
########################################################################################

try:
    
    # CREATE A KAFKA PRODUCER
    kafka_producer = create_kafka_producer()

    # LOAD THE DATASET OF FRESH DATA
    fresh_dataset: list[dict] = misc.load_csv(state.dataset_file)
    
    # PUSH THE ROWS INTO KAFKA
    # NOTE THAT ALL NUMBERS ARE STRINGIFIED,
    # PRE-PROCESSING SHOULD CONVERT THEM INTO NUMBERS
    for unprocessed_row in fresh_dataset:
        kafka_producer.push_msg(constants.kafka.DATA_REFINERY, unprocessed_row)
        time.sleep(state.injection_cooldown)

# TERMINATE MAIN PROCESS AND KILL HELPER THREADS
except KeyboardInterrupt:
    misc.log('PROCESS MANUALLY KILLED..', True)
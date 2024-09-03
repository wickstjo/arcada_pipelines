import utilz.dataset_utils as dataset_utils
from utilz.misc import log
from utilz.kafka_utils import create_producer
from utilz.types import DICT_NAMESPACE
import time

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # WHAT KAFKA TOPIC SHOULD WE PUSH DATA INTO?
    'output_topic': 'input_data',

    # HOW LONG TO WAIT BETWEEN EVENTS
    'dataset': 'foo.csv',
    'cooldown': 0.5,
})

########################################################################################
########################################################################################

try:
    
    # CREATE A KAFKA PRODUCER
    # LOAD THE CSV DATASET INTO AN ARRAY OF DICTS
    kafka_producer = create_producer()
    dataset = dataset_utils.load_csv(config.dataset)
    
    # PUSH THE ROWS INTO KAFKA
    # NOTE THAT ALL NUMBERS ARE STRINGIFIED,
    # PRE-PROCESSING SHOULD CONVERT THEM INTO NUMBERS
    for item in dataset:
        kafka_producer.push_msg(config.output_topic, item)
        time.sleep(config.cooldown)

# TERMINATE MAIN PROCESS AND KILL HELPER THREADS
except KeyboardInterrupt:
    log('KAFKA FEEDING MANUALLY KILLED..', True)
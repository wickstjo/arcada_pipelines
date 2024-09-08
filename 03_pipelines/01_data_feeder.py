import utils.dataset_utils as dataset_utils
from utils.misc import log
from utils.types import TO_NAMESPACE
from utils.kafka_utils import create_producer
import time

########################################################################################
########################################################################################

local_config = TO_NAMESPACE({

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
    dataset = dataset_utils.load_csv(local_config.dataset)
    
    # PUSH THE ROWS INTO KAFKA
    # NOTE THAT ALL NUMBERS ARE STRINGIFIED,
    # PRE-PROCESSING SHOULD CONVERT THEM INTO NUMBERS
    for item in dataset:
        kafka_producer.push_msg(local_config.output_topic, item)
        time.sleep(local_config.cooldown)

# TERMINATE MAIN PROCESS AND KILL HELPER THREADS
except KeyboardInterrupt:
    log('KAFKA FEEDING MANUALLY KILLED..', True)
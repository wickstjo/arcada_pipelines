import utils.dataset_utils as dataset_utils
import utils.misc as misc
from utils.kafka_utils import create_producer
import time

########################################################################################
########################################################################################

class create_state:
    def __init__(self):

        # RELEVANT KAFKA TOPICS
        self.output_topic: str = 'data_refinery'

        # DATASET & INJECTION PARAMS
        self.dataset: str = 'foo.csv'
        self.cooldown: float = 0.5

state = create_state()

########################################################################################
########################################################################################

try:
    
    # CREATE A KAFKA PRODUCER
    # LOAD THE CSV DATASET INTO AN ARRAY OF DICTS
    kafka_producer = create_producer()
    dataset = dataset_utils.load_csv(state.dataset)
    
    # PUSH THE ROWS INTO KAFKA
    # NOTE THAT ALL NUMBERS ARE STRINGIFIED,
    # PRE-PROCESSING SHOULD CONVERT THEM INTO NUMBERS
    for item in dataset:
        kafka_producer.push_msg(state.output_topic, item)
        time.sleep(state.cooldown)

# TERMINATE MAIN PROCESS AND KILL HELPER THREADS
except KeyboardInterrupt:
    misc.log('FEEDING MANUALLY KILLED..', True)
from utilz.kafka_utils import create_consumer
from utilz.misc import custom_deserializer, log, create_lock
import json

########################################################################################
########################################################################################

# DESERIALIZE BYTES COMING FROM KAFKA
# INVERSE OF THE PRODUCERS SERIALIZER
def your_deserializer(raw_bytes: bytes) -> list[bool, dict|str]:
    try:
        json_dict = json.loads(raw_bytes.decode('UTF-8'))
        return True, json_dict
    except:
        return False, 'DESERIALIZATION ERROR'

########################################################################################
########################################################################################

# ON EVENT, DO..
def process_event(parsed_data: dict):
    print(parsed_data)

########################################################################################
########################################################################################

def run():

    args = {
        'input_topic': 'model_evaluation'
    }

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args['input_topic'])
    thread_lock = create_lock()

    # MAKE SURE KAFKA CONNECTIONS ARE OK
    if not kafka_consumer.connected():
        return

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_consumer.poll_next(1, thread_lock, your_deserializer, process_event)

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        log('WORKER MANUALLY KILLED..', True)

run()
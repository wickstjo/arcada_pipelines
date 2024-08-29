from utilz.kafka_utils import create_consumer_producer, create_consumer
from utilz.misc import log, create_lock
from typing import Callable, Dict, Any

########################################################################################
########################################################################################

def start_consumer_producer(client_args: Dict[str, Any], handle_event: Callable[[Any], Dict[str, Any]]):

    # REQUIRED ARG KEYS
    required_args = ['input_topic', 'output_topic']

    # MAKE SURE THEY'RE DEFINED
    for arg in required_args:
        if arg not in client_args:
            return log(f'MANDATORY ARG ({arg}) NOT DEFINED, ABORTING..')

    # CREATE THE KAKFA CLIENT & CONTROL LOCK
    kafka_client = create_consumer_producer(**client_args)
    thread_lock = create_lock()

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_client.poll_next(thread_lock, handle_event)

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        log('WORKER MANUALLY KILLED..', True)

########################################################################################
########################################################################################

def start_consumer(client_args: Dict[str, Any], handle_event: Callable[[Any], None]):

    # REQUIRED ARG KEYS
    required_args = ['input_topic']

    # MAKE SURE THEY'RE DEFINED
    for arg in required_args:
        if arg not in client_args:
            return print(f'MANDATORY ARG ({arg}) NOT DEFINED, ABORTING..')

    # CREATE THE KAKFA CLIENT & CONTROL LOCK
    kafka_client = create_consumer(**client_args)
    thread_lock = create_lock()

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_client.poll_next(thread_lock, handle_event)

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        log('WORKER MANUALLY KILLED..', True)

########################################################################################
########################################################################################
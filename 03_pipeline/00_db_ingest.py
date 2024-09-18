from dataclasses import dataclass
import funcs.dataset_utils as dataset_utils
from funcs.cassandra_utils import create_cassandra_instance
from funcs.thread_utils import create_thread_pool
import funcs.misc as misc
import funcs.types as types

########################################################################################
########################################################################################

@dataclass(frozen=True)
class state:
    n_threads: int = 8
    report_breakpoint: int = 100
    source_dataset: str = 'finance_historical.csv'
    cassandra_table: str = 'john.refined_stock_data'

########################################################################################
########################################################################################

def thread_routine(pool_resources: list):
    try:
        
        # EXTRACT THE THREADPOOL RESOURCES
        nth_thread, process_beacon, mutex, counter = pool_resources

        # SELECT CASSANDRA CLIENT & FIRST DATASET INDEX
        cassandra = cassandra_clients[nth_thread - 1]
        dataset_length = len(dataset)
        next_index = nth_thread - 1

        # LOOP UNTIL LOCK IS KILLED OR DATASET ENDS
        while process_beacon.is_active() and (next_index < dataset_length):

            # PARSE THE NEXT DATASET ROW & WRITE IT TO THE DB
            sanitized_row: dict = misc.validate_dict(dataset[next_index], types.REFINED_STOCK_DATA)
            cassandra.write(state.cassandra_table, sanitized_row)

            # JUMP TO NEXT INDEX & INCREMENT THREADPOOL COUNTER
            next_index += state.n_threads
            counter.increment(announce_every=state.report_breakpoint)
    
    except Exception as error:
        with mutex:
            misc.log(f'THREAD ({nth_thread}) ERROR: {error}')
            process_beacon.kill()

########################################################################################
########################################################################################

try:

    # CREATE A CASSANDRA CLIENT FOR EACH THREAD
    # THEN, LOAD THE CSV DATASET
    cassandra_clients = [create_cassandra_instance(HIDE_LOGS=True) for _ in range(state.n_threads)]
    dataset = dataset_utils.load_csv(state.source_dataset)

    # RESET THE OLD TABLE CONTENT
    cassandra_clients[0].query(f'TRUNCATE {state.cassandra_table}')

    # CREATE & START A THREAD POOL
    # THEN, WAIT FOR THE THREADS TO FINISH
    thread_pool = create_thread_pool(state.n_threads, thread_routine)
    thread_pool.launch()

# INTENTIONALLY TERMINATE MAIN PROCESS AND HELPER THREADS
except KeyboardInterrupt:
    thread_pool.kill()
    misc.log('PROCESS MANUALLY KILLED..', True)
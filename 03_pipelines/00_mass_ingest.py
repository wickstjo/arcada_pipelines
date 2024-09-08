import utils.dataset_utils as dataset_utils
from utils.cassandra_utils import create_cassandra_instance
from utils.thread_utils import create_thread_pool
from utils.misc import log
from utils.types import TO_NAMESPACE
import random

########################################################################################
########################################################################################

local_config = TO_NAMESPACE({

    # HOW MANY THREADS SHOULD WE USE?
    'n_threads': 4,
    'report_breakpoint': 10,

    # WHAT DATASET FILE SHOULD WE INGEST?
    # WHAT TABLE DO YOU WANT TO WRITE DATA TO?
    'source_dataset': 'foo.csv',
    'cassandra_table': 'testing_keyspace.testing_table',
})

########################################################################################
########################################################################################

# SHARED THREAD ROUTINE
def thread_routine(pool_resources):
    try:
        
        # EXTRACT THE THREADPOOL RESOURCES
        nth_thread, beacon, mutex, counter = pool_resources

        # AUXILLARY
        cassandra = cassandra_clients[nth_thread - 1]
        dataset_length = len(dataset)
        next_index = nth_thread - 1

        # PARSE RAW DATASET ROWS INTO SANITIZED ROWS
        def parse_row(raw_row):
            return {
                'timestamp': int(random.uniform(10**2, 10**4)),
                'open': float(raw_row['open']),
                'close': float(raw_row['close']),
                'high': float(raw_row['high']),
                'low': float(raw_row['low']),
                'volume': int(float(raw_row['volume'])),
            }

        # LOOP UNTIL LOCK IS KILLED OR DATASET ENDS
        while beacon.is_active() and (next_index < dataset_length):

            # PARSE THE NEXT DATASET ROW & WRITE IT TO THE DB
            sanitized_row = parse_row(dataset[next_index])
            cassandra.write(local_config.cassandra_table, sanitized_row)

            # JUMP TO NEXT INDEX & INCREMENT THREADPOOL COUNTER
            next_index += local_config.n_threads
            counter.increment(announce_every=10)
    
    except Exception as error:
        with mutex:
            log(f'THREAD ({nth_thread}) ERROR: {error}')

########################################################################################
########################################################################################

try:

    # CREATE A CASSANDRA CLIENT FOR EACH THREAD
    # THEN, LOAD THE CSV DATASET
    cassandra_clients = [create_cassandra_instance() for _ in range(local_config.n_threads)]
    dataset = dataset_utils.load_csv(local_config.source_dataset)

    # CREATE & START A THREAD POOL
    # THEN, WAIT FOR THE THREADS TO FINISH
    thread_pool = create_thread_pool(local_config.n_threads, thread_routine)
    thread_pool.launch()

# INTENTIONALLY TERMINATE MAIN PROCESS AND HELPER THREADS
except KeyboardInterrupt:
    thread_pool.kill()
    log('PROCESS MANUALLY KILLED..', True)
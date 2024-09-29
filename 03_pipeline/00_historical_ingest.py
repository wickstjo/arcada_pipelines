from funcs import cassandra_utils, redis_utils
from funcs import thread_utils, misc, constants, types

class pipeline_component:
    def __init__(self, thread_beacon):
        
        # HOW MANY THREADS SHOULD WE USE?
        self.n_threads: int = 8

        # CREATE INSTANCED CLIENTS
        self.cassandra_clients = [cassandra_utils.create_instance(HIDE_LOGS=True) for _ in range(self.n_threads)]
        self.redis = redis_utils.create_instance()

        # I ASSUME THE INTENTION HERE IS TO FRESHLY RE-RUN AN EXPERIMENT
        # THEREFORE, RESET OLD DB & CACHE RESOURCES
        self.cassandra_clients[0].query(f'TRUNCATE {constants.cassandra.STOCKS_TABLE}')
        self.redis.set(constants.redis.MODEL_PIPELINES, {})
        misc.log('NUKED DATABASES & REDIS CACHE')

        # LOAD THE DATASET
        source_dataset: str = 'datasets/finance_historical.csv'
        self.dataset = misc.load_csv(source_dataset)

        # FOR TRACKING & BINDING WORKER THREADS
        self.thread_beacon = thread_beacon
        self.counter = thread_utils.create_counter(announce_every=100)

        # CREATE & START WORKER THREADS
        threads = [thread_utils.start_thread(self.thread_routine, (nth,)) for nth in range(self.n_threads)]

        # WAIT FOR EACH THREAD TO FINISH THEIR JOB
        [thread.join() for thread in threads]

    ########################################################################################
    ########################################################################################

    def thread_routine(self, nth_thread):
        try:

            # SELECT CASSANDRA CLIENT & FIRST DATASET INDEX
            cassandra = self.cassandra_clients[nth_thread - 1]
            dataset_length = len(self.dataset)
            next_index = nth_thread - 1

            # LOOP UNTIL LOCK IS KILLED OR DATASET ENDS
            while self.thread_beacon.is_active() and (next_index < dataset_length):

                # PARSE THE NEXT DATASET ROW & WRITE IT TO THE DB
                sanitized_row: dict = misc.validate_dict(self.dataset[next_index], types.REFINED_STOCK_DATA)
                cassandra.write(constants.cassandra.STOCKS_TABLE, sanitized_row)

                # JUMP TO NEXT INDEX & INCREMENT THREADPOOL COUNTER
                next_index += self.n_threads
                self.counter.increment()
        
        # IF ONE THREAD FAILS, KILL EVERYTHING ELSE
        except Exception as error:
            misc.log(f'THREAD ({nth_thread}) ERROR: {error}')
            self.thread_beacon.kill()

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component, poll=False)
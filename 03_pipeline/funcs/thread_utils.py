from threading import Thread, Semaphore
from typing import Callable
from funcs import misc, constants
import time

global_config = constants.global_config()

########################################################################################################
########################################################################################################

def create_mutex():
    return Semaphore(1)

########################################################################################################
########################################################################################################

class create_thread_pool:
    def __init__(self, num_threads: int, thread_routine: Callable, routine_args: tuple = ()):
        self.threads = []

        # THREAD-SAFETY RESOURCES
        self.beacon = create_process_beacon()
        self.mutex = create_mutex()
        self.counter = create_counter()

        # CREATE THE THREAD-POOL
        for nth in range(num_threads):
            final_args = routine_args + ([nth+1, self.beacon, self.mutex, self.counter],)
            thread = Thread(target=thread_routine, args=final_args)
            self.threads.append(thread)
        
    # START THREAD POOL AND WAIT FOR THREADS TO FINISH
    def launch(self):
        self.start()
        self.join()

    # ASYNCHRONOUSLY START THE THREAD-POOL
    def start(self):
        misc.log(f'STARTING THREAD-POOL (num_threads={len(self.threads)})')
        [thread.start() for thread in self.threads]

        # TRACK WHEN THE PROCESSING STARTED
        self.work_started = time.time()

    # SYNCHRONOUSLY WAIT FOR EACH THREAD TO FINISH
    def join(self):
        [thread.join() for thread in self.threads]
        
        # COMPUTE HOW LONG THE PROCESSING TOOK
        work_ended = time.time()
        delta_time = round(work_ended - self.work_started, 3)

        with self.mutex:
            misc.log(f'THREAD-POOL FINISHED WORKING (count={self.counter.current()}, time={delta_time})')

    # KILL BEACON, WHICH KILLS THE HELPER THREADS
    def kill(self):
        self.beacon.kill()

########################################################################################################
########################################################################################################

# THREAD LOCK TO KILL HELPER THREADS
class create_process_beacon:
    def __init__(self):
        self.lock = True

    def __del__(self):
        self.kill()
    
    def is_active(self):
        return self.lock
    
    def kill(self):
        self.lock = False

########################################################################################################
########################################################################################################

# THREAD-SAFE COUNTER
class create_counter:
    def __init__(self):
        self.value = 0
        self.mutex = create_mutex()
    
    def current(self):
        with self.mutex:
            return self.value
    
    def increment(self, announce_every=0):
        with self.mutex:
            self.value += 1

            if (announce_every > 0) and (self.value % announce_every) == 0:
                misc.log(f'THREAD-POOL COUNTER HAS REACHED {self.value}')

########################################################################################################
########################################################################################################

def start_coordinator(create_pipeline_state):

    # CREATE A PROCESS BEACON TO BIND THREAD ROUTINES
    process_beacon = create_process_beacon()

    try:
        # INSTANTIATE THE PIPELINE STATE
        state = create_pipeline_state(process_beacon)

        while process_beacon.is_active():
            time.sleep(global_config.pipeline.polling_cooldown)

    except AssertionError as error:
        misc.log(f'{error}')
    
    # KILL ALL HELPER-THREADS WHEN MAIN THREAD DIES
    except KeyboardInterrupt:
        misc.log('[COORDINATOR] MANUALLY INTERRUPTED..', True)
        process_beacon.kill()

    except Exception as error:
        misc.log(f'{error}')

########################################################################################################
########################################################################################################

def start_thread(func, _args=(), _daemon=False):
    thread = Thread(target=func, args=_args)
    thread.daemon = _daemon
    thread.start()
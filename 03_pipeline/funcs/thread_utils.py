from threading import Thread, Semaphore
from funcs.misc import log
from typing import Callable
import time

########################################################################################################
########################################################################################################

class create_thread_pool:
    def __init__(self, num_threads: int, thread_routine: Callable, routine_args: tuple = ()):
        self.threads = []

        # THREAD-SAFETY RESOURCES
        self.beacon = create_process_beacon()
        self.mutex = Semaphore(1)
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
        log(f'STARTING THREAD-POOL (num_threads={len(self.threads)})')
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
            log(f'THREAD-POOL FINISHED WORKING (count={self.counter.current()}, time={delta_time})')

    # KILL BEACON, WHICH KILLS THE HELPER THREADS
    def kill(self):
        self.beacon.kill()

########################################################################################################
########################################################################################################

# THREAD LOCK TO KILL HELPER THREADS
class create_process_beacon:
    def __init__(self):
        self.lock = True
    
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
        self.mutex = Semaphore(1)
    
    def current(self):
        with self.mutex:
            return self.value
    
    def increment(self, announce_every=0):
        with self.mutex:
            self.value += 1

            if (announce_every > 0) and (self.value % announce_every) == 0:
                log(f'THREAD-POOL COUNTER HAS REACHED {self.value}')
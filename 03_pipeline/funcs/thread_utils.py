from threading import Thread, Semaphore
from typing import Callable
import funcs.misc as misc
import time

########################################################################################################
########################################################################################################

def background_process(event_loop: Callable, cooldown: int, process_beacon):

    # WRAP THE THREAD IN A BEACON-BOUND LOOP
    def thread_wrapper():
        try:
            while process_beacon.is_active():
                event_loop()
                time.sleep(cooldown)

        # IF THE BACKGROUND THREAD CRASHES, KILL THE MAIN THREAD TOO
        except Exception as error:
            misc.log(f'BACKGROUND THREAD CRASHED: {error}')
            process_beacon.kill()

    # CREATE & START THE THREAD
    thread = Thread(target=thread_wrapper, args=())
    thread.start()

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
import redis, json, time
from funcs import thread_utils, constants, misc

# FETCH NECESSARY INFO FROM YAML CONFIG
global_config = constants.global_config()
REDIS_HOST, REDIS_PORT = global_config.cluster.redis_broker.split(':')
# VERBOSE = global_config.backend.verbose_logging

class create_instance:
    def __init__(self):
        self.instance = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)
    
    def __del__(self):

        # KILL ANY ACTIVE CONSUMER
        if hasattr(self, 'pubsub'):
            self.pubsub.unsubscribe()
            self.pubsub.close()

        self.instance.close()
        misc.log('[REDIS] INSTANCE TERMINATED')
    
    ########################################################################################################
    ########################################################################################################
    
    def set(self, key: str, value: str|int|float|dict):
        assert isinstance(key, str), '[REDIS] THE KEY MUST BE A STRING'
        assert isinstance(value, (str, int, float, dict)), '[REDIS] VALUE TYPE MUST BE STR|INT|FLOAT|DICT'
        temp_value = value

        # STRINGIFY DICTS
        if type(value) == dict:
            temp_value = json.dumps(temp_value)
        
        result = self.instance.set(key, temp_value)
        assert result == 1, f"[REDIS] SETTING KEY '{key}' FAILED"

    ########################################################################################################
    ########################################################################################################

    def parse_value(self, raw_value):
        try:
            # DECODE IT
            stringified_value = raw_value.decode('utf-8')

            # IS IT AN INTEGER?
            if stringified_value.isdigit():
                return int(stringified_value)

            # IS IT A FLOAT?
            try:
                return float(stringified_value)
            except:
                pass

            # IS IT JSON?
            try:
                return json.loads(stringified_value)
            except:
                pass
            
            # OTHERWISE, ITS A STRING
            return stringified_value
        
        except Exception as error:
            print(f'[REDIS PARSING ERROR] {error}')

    ########################################################################################################
    ########################################################################################################
    
    def get(self, key: str):
        assert isinstance(key, str), '[REDIS] THE KEY MUST BE A STRING'

        # MAKE SURE THE VALUE EXISTS
        raw_value = self.instance.get(key)
        assert raw_value != None, f"[REDIS] KEY '{key}' HAS NO VALUE"
        
        # DECODE & PARSE IT
        return self.parse_value(raw_value)

    ########################################################################################################
    ########################################################################################################
    
    def exists(self, key: str):
        assert isinstance(key, str), '[REDIS] THE KEY MUST BE A STRING'
        return True if self.instance.exists(key) else False
    
    ########################################################################################################
    ########################################################################################################
    
    # MAKE SURE THE KEY EXISTS, THEN TRY TO DELETE IT
    def delete(self, key: str):
        assert isinstance(key, str), '[REDIS] THE KEY MUST BE A STRING'
        assert self.exists(key), f"[REDIS] KEY '{key}' DOES NOT EXIST"
        assert self.instance.delete(key) == 1, f"[REDIS] KEY '{key}' DELETION FAILED"
        
    ########################################################################################################
    ########################################################################################################

    def subscribe(self, key: str, callback_func, process_beacon):
        assert isinstance(key, str), '[REDIS] THE KEY MUST BE A STRING'
        assert self.exists(key), f"[REDIS] KEY '{key}' DOES NOT EXIST"

        def consume_events():
            previous_value = None
            misc.log(f'[REDIS] STARTED POLLING ({key})')

            while process_beacon.is_active():
                try:
                    current_value = self.get(key)
                    
                    # IF THE VALUE HAS CHANGED -- RUN CALLBACK FUNC
                    if current_value != previous_value:
                        callback_func()
                        previous_value = current_value
                    
                    time.sleep(global_config.pipeline.polling_cooldown)

                except Exception as error:
                    misc.log(f'[REDIS] CONSUME ERROR: {error}')
                    
        # START CONSUMING EVENTS IN BACKGROUND THREAD
        thread_utils.start_thread(consume_events)
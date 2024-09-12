# pip install redis
import redis, json, time
from threading import Thread
import funcs.misc as misc

########################################################################################################
########################################################################################################

class create_redis_instance:
    def __init__(self, process_beacon):
        self.beacon = process_beacon
        self.instance = redis.StrictRedis(host='localhost', port=6379, db=0)

    ########################################################################################################
    ########################################################################################################

    # DATA SERIALIZER: JSON/DICT => BYTES
    def json_serializer(self, json_data: dict) -> bytes:
        try:
            return json.dumps(json_data).encode('UTF-8')
        except Exception as error:
            raise Exception(f'[REDIS] SERIALIZATION ERROR: {error}')

    ########################################################################################################
    ########################################################################################################

    # DATA DESERIALIZER: BYTES => JSON DICT
    def json_deserializer(self, raw_bytes: bytes) -> dict:
        try:
            return json.loads(raw_bytes.decode('UTF-8'))
        except Exception as error:
            raise Exception(f'[REDIS] DESERIALIZATION ERROR: {error}')

    ########################################################################################################
    ########################################################################################################

    # PUSH SERIALIZED DICT TO REDIS CHANNEL
    def publish(self, redis_channel: str, input_data: dict):
        try:
            serialized_data = self.json_serializer(input_data)
            self.instance.publish(redis_channel, serialized_data)
            misc.log(f'[REDIS] PUSHED EVENT ({redis_channel})')
        except Exception as error:
            raise Exception(f'[REDIS] PUSH ERROR: {error}')

    ########################################################################################################
    ########################################################################################################

    # SUBSCRIBE TO REDIS EVENTS
    def subscribe(self, redis_channel: str|list[str], handle_event):
        misc.log(f'[REDIS] STARTED POLLING ({redis_channel})')

        # PUSH SERIALIZED DICT TO REDIS CHANNEL
        def thread_routine():

            # SUBSCRIBE TO CHANNEL
            pubsub = self.instance.pubsub()
            pubsub.subscribe(redis_channel)
            
            # START POLLING EVENTS
            while self.beacon.is_active():
                try:
                    next_event = pubsub.get_message()
                    if next_event and next_event['type'] == 'message':

                        # DESERIALIZE EVENT COMPONENTS
                        deserialized_channel = next_event['channel'].decode('UTF-8')
                        deserialized_data = self.json_deserializer(next_event['data'])

                        misc.log(f'[REDIS] EVENT RECEIVED ({deserialized_channel})')

                        # RUN CALLBACK FUNC
                        try:
                            handle_event(deserialized_channel, deserialized_data)
                        except Exception as error:
                            misc.log(f'[REDIS] CALLBACK ERROR: {error}')

                        misc.log('[REDIS] EVENT HANDLED')

                    time.sleep(0.2)
                except Exception as error:
                    raise Exception(f'[REDIS] POLLING ERROR: {error}')

            misc.log(f'[REDIS] POLLING WAS MANUALLY KILLED')

        # CREATE & START THE BACKGROUND THREAD
        thread = Thread(target=thread_routine, args=())
        thread.start()

########################################################################################################
########################################################################################################

# try:
#     beacon = misc.create_process_beacon()
#     foo = create_redis_instance(beacon)
#     foo.subscribe('events_channel', lambda x: print(x))
# except KeyboardInterrupt:
#     print('PROCESS MANUALLY KILLED..')
#     beacon.kill()
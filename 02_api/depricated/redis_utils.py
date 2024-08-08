import redis
import json

class cache_instance():
    def __init__(self):
        self.client = redis.Redis(host='redis_cache', port=6379, db=0)

    # READ FROM CACHE
    def read(self, key):
        content = self.client.get(key)

        # NO CACHE CONTENT
        if content == None:
            return [False, {}]

        # TRY TO DESERIALIZE
        try:
            deserialized = json.loads(content.decode('UTF-8'))
            return [True, deserialized]
        
        # CATCH EXCEPTIONS
        except:
            print('CACHE SERIALIZATION ERROR')
            return [False, {}]

    # WRITE INTO CACHE
    def write(self, key, data):
        if type(data) == dict:
            serialized = json.dumps(data).encode('UTF-8')
            self.client.set(key, serialized)
        else:
            print('ERROR, NON-DICT INPUT')

    def check(self, key):
        content = self.client.get(key)

        if content == None:
            return False
            
        return True
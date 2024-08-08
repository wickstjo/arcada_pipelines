import hashlib
import json

def hash_dict(input_dict):
    m = hashlib.sha256()

    encoded = json.dumps(input_dict).encode('utf-8')
    m.update(encoded)
    m.digest()
    
    return m.hexdigest()

def load_json(path):
    with open(path) as json_file:
        return json.load(json_file)
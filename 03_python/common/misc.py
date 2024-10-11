import yaml, time, json, random
from datetime import datetime
from types import SimpleNamespace

########################################################################################################
########################################################################################################

# TIMESTAMPED PRINT STATEMENT
def log(msg, with_break=False):
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S.%f")[:-3]

    if with_break:
        print(f'\n[{timestamp}]\t {msg}', flush=True)
    else:
        print(f'[{timestamp}]\t {msg}', flush=True)

########################################################################################################
########################################################################################################

def load_yaml(file_path, ns=False):
    with open(file_path, 'r') as file:
        data_dict: dict = yaml.safe_load(file)
        if ns: return TO_NAMESPACE(data_dict)
        return data_dict
    
def save_yaml(file_path, data_dict):
    with open(f'{file_path}', 'w') as file:
        yaml.dump(data_dict, file, default_flow_style=False)

########################################################################################################
########################################################################################################

# CONVERT DICT TO CLASS NAMESPACE
def TO_NAMESPACE(d):
    if isinstance(d, dict):
        # Recursively convert the dictionary to a namespace
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = TO_NAMESPACE(value)
            elif isinstance(value, list):
                # Process each item in the list
                d[key] = [TO_NAMESPACE(item) if isinstance(item, dict) else item for item in value]
        return SimpleNamespace(**d)
    elif isinstance(d, list):
        # Process a list if the outermost structure is a list
        return [TO_NAMESPACE(item) if isinstance(item, dict) else item for item in d]
    else:
        # If d is neither a dict nor a list, return it as is
        return d
    
########################################################################################################
########################################################################################################

def pprint(data: dict):
    assert type(data) == dict, 'YOU CAN ONLY PRETTY PRINT DICTS'
    print(json.dumps(data, indent=4))

########################################################################################################
########################################################################################################

def timeout_range(min, max):
    duration = random.uniform(min, max)
    time.sleep(duration)

########################################################################################################
########################################################################################################
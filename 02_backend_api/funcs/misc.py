from types import SimpleNamespace as sn
import yaml
from datetime import datetime

########################################################################################################
########################################################################################################

# CONVERT DICT TO CLASS NAMESPACE
def DICT_NAMESPACE(d):
    if isinstance(d, dict):
        # Recursively convert the dictionary to a namespace
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = DICT_NAMESPACE(value)
            elif isinstance(value, list):
                # Process each item in the list
                d[key] = [DICT_NAMESPACE(item) if isinstance(item, dict) else item for item in value]
        return sn(**d)
    elif isinstance(d, list):
        # Process a list if the outermost structure is a list
        return [DICT_NAMESPACE(item) if isinstance(item, dict) else item for item in d]
    else:
        # If d is neither a dict nor a list, return it as is
        return d

########################################################################################################
########################################################################################################

def load_yaml(file_path, ns=False):
    with open(file_path, 'r') as file:
        data_dict: dict = yaml.safe_load(file)
        if ns: return DICT_NAMESPACE(data_dict)
        return data_dict

def save_yaml(file_path, data_dict):
    with open(f'{file_path}', 'w') as file:
        yaml.dump(data_dict, file, default_flow_style=False)
    
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
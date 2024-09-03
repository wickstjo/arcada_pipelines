import csv, yaml
from datetime import datetime
from types import SimpleNamespace as sn

########################################################################################################
########################################################################################################

# LOAD CSV INTO DICT ARRAY
def load_csv(file_name):
    container = []
    file_path = f'datasets/{file_name}'

    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            container.append(row)

    return container

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

# THREAD LOCK TO KILL HELPER THREADS
class create_lock:
    def __init__(self):
        self.lock = True
    
    def is_active(self):
        return self.lock
    
    def kill(self):
        self.lock = False

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

# LOAD SYSCONFIG FROM ROOT YAML FILE
def load_global_config(file_path):
    with open(file_path, 'r') as file:
        data_dict = yaml.safe_load(file)

        # RETURN AS A NAMESPACE RATHER THAN A DICT
        return DICT_NAMESPACE(data_dict)
    
########################################################################################################
########################################################################################################
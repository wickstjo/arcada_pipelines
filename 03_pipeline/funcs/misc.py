import csv, yaml
from datetime import datetime
from types import SimpleNamespace

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

# VALIDATE AN INPUT DICT BASED ON A REFERENCE DICT
def validate_dict(input_data: dict, reference: dict):
    container = {}

    # REFERENCE DICT: KEY_NAME => TYPE_FUNC
    for prop_name, type_cast_func in reference.items():

        # MAKE SURE DICT KEY EXIST
        if prop_name not in input_data:
            raise Exception(f'KEY ERROR: MISSING PROPERTY ({prop_name})')
        
        # MAKE SURE EVERY VALUE CAN BE CAST TO ITS EXPECTED TYPE
        try:
            input_value = input_data[prop_name]
            container[prop_name] = type_cast_func(input_value)

        except Exception as error:
            raise Exception(f'CASTING ERROR (prop: {prop_name}): {error}')
        
    return container

########################################################################################################
########################################################################################################

# LOAD SYSCONFIG FROM ROOT YAML FILE
# STATIC FILEREF SHOULD WORK..?
def load_global_config():
    with open('../00_configs/global_config.yaml', 'r') as file:
        data_dict = yaml.safe_load(file)

        # RETURN AS A NAMESPACE RATHER THAN A DICT
        return TO_NAMESPACE(data_dict)

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
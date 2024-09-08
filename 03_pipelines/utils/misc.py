import csv, yaml
from datetime import datetime
from utils.types import TO_NAMESPACE

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

# LOAD SYSCONFIG FROM ROOT YAML FILE
# STATIC FILEREF SHOULD WORK..?
def load_global_config():
    with open('../00_configs/global_config.yaml', 'r') as file:
        data_dict = yaml.safe_load(file)

        # RETURN AS A NAMESPACE RATHER THAN A DICT
        return TO_NAMESPACE(data_dict)
    
########################################################################################################
########################################################################################################
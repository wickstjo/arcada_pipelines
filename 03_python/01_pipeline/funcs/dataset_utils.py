import csv

########################################################################################################
########################################################################################################

# LOAD CSV INTO DICT ARRAY
def load_csv(file_path: str):
    container = []

    with open(f'../01_datasets/{file_path}', mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            container.append(row)

    return container
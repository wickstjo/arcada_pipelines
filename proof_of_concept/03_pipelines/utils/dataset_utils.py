import csv

###################################################################################################
###################################################################################################

# LOAD CSV INTO DICT ARRAY
def load_csv(file_name):
    container = []
    file_path = f'datasets/{file_name}'

    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            container.append(row)

    return container

###################################################################################################
###################################################################################################
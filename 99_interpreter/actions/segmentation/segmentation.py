import math

##############################################################################################################
##############################################################################################################

def train_test_validation_split(training_config, dataset, pipeline):
    segment_ratios = training_config['segmentation']
    label_column = training_config['label_column']

    container = {}
    old_limit = 0
    dataset_length = len(dataset)

    # TRACK HOW MANY VALUES ARE NEEDED TO CREATE A
    # FULL ROW OF FEATURES
    min_batch_size = None

    # LOOP THROUGH EACH SEQUENTIAL SEGMENT
    for block in segment_ratios:
        for segment_name, segment_percentage in block.items():

            # HOW MANY ROWS DOES THE PERCENTAGE TRANSLATE TO?
            num_rows = math.ceil(dataset_length * segment_percentage)
            new_limit = min(old_limit + num_rows, dataset_length)

            # SELECT THE SUBSET & GENERATE LABELS FOR IT
            subset = dataset[old_limit:new_limit]
            labels = extract_labels(subset, pipeline, label_column)

            # PAIR SUBSET WITH ITS LABELS
            container[segment_name] = data_block(subset, labels)

            # MEASURE LENGTH DELTA CAUSED BY NAN VALUES
            length_delta = len(subset) - len(labels)

            # SET INITIAL BATCH SIZE
            if min_batch_size == None:
                min_batch_size = length_delta

            # MAKE SURE BATCH SIZE IS CONSISTENT FOR ALL WINDOWS
            assert length_delta == min_batch_size, 'INCONSISTENT MIN WINDOW SIZE'

            # UPDATE LIMIT
            old_limit = new_limit

    return container, min_batch_size

##############################################################################################################
##############################################################################################################

class data_block:
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

##############################################################################################################
##############################################################################################################

# APPLY PIPELINE FEATURES ON SUBSET
# AND EXTRACT LABEL COLUMN FROM THE RESULTING DATAFRAME
def extract_labels(dataset, pipeline, label_column):
    cloned_dataset = [x for x in dataset]

    for block in pipeline:
        _, feature = block
        cloned_dataset = feature.transform(cloned_dataset)

    return cloned_dataset[label_column].tolist()

##############################################################################################################
##############################################################################################################
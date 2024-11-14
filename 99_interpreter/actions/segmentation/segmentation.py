import math

def segment_dataset(segment_ratios: list[dict], dataset: list[dict]):
    assert isinstance(segment_ratios, list), f"ARG 'segment_ratios' MUST BE OF TYPE DICT"
    assert isinstance(dataset, list), f"ARG 'dataset' MUST BE OF TYPE LIST[DICT]"

    container = {}
    old_limit = 0
    dataset_length = len(dataset)

    # LOOP THROUGH EACH SEQUENTIAL SEGMENT
    for block in segment_ratios:
        for segment_name, segment_percentage in block.items():

            # HOW MANY ROWS DOES THE PERCENTAGE TRANSLATE TO?
            num_rows = math.ceil(dataset_length * segment_percentage)
            new_limit = min(old_limit + num_rows, dataset_length)

            # ALLOCATE THE SUBSET
            container[segment_name] = dataset[old_limit:new_limit]
            old_limit = new_limit

    return container

#######################################
### EXAMPLE USAGE

# result = segment_dataset([
#     { 'test': 0.32 },
#     { 'validate': 0.118 },
#     { 'train': 0.562 },
# ], [x for x in range(420)])

# print(result)
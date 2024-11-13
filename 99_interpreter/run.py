from common import misc, testing
# from actions.load_dataset import load_dataset

# LOAD EXPERIMENT CONFIG AS WELL AS THE REFERENCE YAML
experiment_config: dict = misc.load_yaml('config.yaml')

# TODO COMPARE USER_CONFIG WITH REF_CONFIG
# TODO COMPARE USER_CONFIG WITH REF_CONFIG
# TODO COMPARE USER_CONFIG WITH REF_CONFIG

# LOAD THE DATASET
# dataset: list[dict] = fetch_dataset(**experiment_config['dataset'])


# TEST DATASET LOADING
dataset_config: dict = experiment_config['dataset']
testing.run_tests('load_dataset', dataset_config)

# TEST DATA SEGMENTATION
segmentation_config: dict = experiment_config['segmentation']
testing.run_tests('segmentation', segmentation_config)
from common import misc, validation, testing
from actions.load_dataset import load_dataset

# LOAD EXPERIMENT CONFIG AS WELL AS THE REFERENCE YAML
experiment_config: dict = misc.load_yaml('config.yaml')
ref_config: dict = misc.load_yaml('ref.yaml')

# MAKE SURE EVERYTHING IS IN ORDER
validation.compare_dicts(experiment_config, ref_config)

# TODO COMPARE USER_CONFIG WITH REF_CONFIG
# TODO COMPARE USER_CONFIG WITH REF_CONFIG
# TODO COMPARE USER_CONFIG WITH REF_CONFIG

# LOAD THE DATASET
# dataset: list[dict] = fetch_dataset(**experiment_config['dataset'])



dataset_config: dict = experiment_config['dataset']
testing.run_tests('load_dataset', dataset_config)
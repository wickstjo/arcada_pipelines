from common import misc, testing

# LOAD EXPERIMENT CONFIG AS WELL AS THE REFERENCE YAML
experiment_config: dict = misc.load_yaml('config.yaml')

##########################################################################
### COMPLETED

# TEST DATASET LOADING
dataset_config: dict = experiment_config['dataset']
testing.run_tests('actions/dataset', dataset_config)

# TEST DATA SEGMENTATION
segmentation_config: dict = experiment_config['segmentation']
testing.run_tests('actions/segmentation', segmentation_config)

# TEST DATA SEGMENTATION
trading_config: dict = experiment_config['trading_strategy']
testing.run_tests('actions/trading_strategies', trading_config)

##########################################################################
### IN DEVELOPMENT

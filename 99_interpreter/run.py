from common import misc, testing
from actions.dataset.load_dataset import load_dataset

def run():
    try:

        # LOAD EXPERIMENT CONFIG AS WELL AS THE REFERENCE YAML
        experiment_config: dict = misc.load_yaml('config.yaml')
        errors: list = []

    ##########################################################################
    ### COMPLETED

        # TEST DATASET LOADING
        dataset_config: dict = experiment_config['dataset']
        # errors += testing.run_tests('actions/dataset', dataset_config)

        # ALL THE DATASET TESTS PASSED
        # MAKE A REAL SAMPLE DATASET AVAILABLE FOR OTHER TESTS
        sample_dataset: list[dict] = load_dataset(dataset_config, unittesting=200)

        # # TEST DATA SEGMENTATION
        # segmentation_config: dict = experiment_config['segmentation']
        # errors += testing.run_tests('actions/segmentation', segmentation_config)

        # # TEST TRADING STRATEGIES
        # trading_config: dict = experiment_config['trading_strategy']
        # errors += testing.run_tests('actions/trading_strategies', trading_config)

    ##########################################################################
    ### IN DEVELOPMENT

        features_config: dict = experiment_config['feature_engineering']

        for feature_name, feature_params in features_config.items():
            errors += testing.run_tests(f'actions/feature_engineering/{feature_name}', {
                **feature_params,
                '_sample_dataset': sample_dataset
            })

    # OTHERWISE, STOP THE EXPERIMENT HERE
    except Exception as error:
        return print(f'\nFATAL EXCEPTION: {error}')
        
run()
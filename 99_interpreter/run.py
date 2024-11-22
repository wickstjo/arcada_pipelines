from common import misc
from actions.data_retrieval.load_dataset import load_dataset
from actions.segmentation.segmentation import train_test_validation_split
from common.constants import feature_repo, scaler_repo, model_repo
from sklearn.pipeline import Pipeline

def run():

    # LOAD EXPERIMENT YAML
    experiment_config: dict = misc.load_yaml('config.yaml')
    pipeline_components = []

    ########################################################################################
    ########################################################################################
    ### LOAD DATASET

    # LOAD A SAMPLE DATASET
    dataset_config: dict = experiment_config['dataset']
    # dataset: list[dict] = load_dataset(dataset_config, unittesting=200)
    dataset: list[dict] = load_dataset(dataset_config)
    print(f'DATASET LENGTH:\t\t{len(dataset)}')

    ########################################################################################
    ########################################################################################
    ### ADD FEATURES

    # ADD FEATURE THAT CONVERS INPUT TO DATAFRAME
    to_df_feature = feature_repo.create('to_dataframe')
    pipeline_components.append(('hidden_input_conversion', to_df_feature))

    # ADD EACH CUSTOM FEATURE
    for nth, block in enumerate(experiment_config['feature_engineering']):
        feature_name = block['feature_name']
        feature_params = block['feature_params']

        feature_instance = feature_repo.create(feature_name, feature_params)
        pipeline_components.append((f'yaml_feature_{nth+1}', feature_instance))

    # ADD FEATURE THAT DROPS ALL NAN ROWS FROM FINAL DATAFRAME
    drop_nan_feature = feature_repo.create('drop_nan_rows')
    pipeline_components.append(('hidden_cleanup', drop_nan_feature))

    ########################################################################################
    ########################################################################################
    ### TRAIN TEST VALIDATION SPLITTING

    model_training = experiment_config['model_training']

    # SPLIT THE DATASET AND LABELS
    # AND FIND WHAT THE MINIMUM BATCH SIZE IS TO
    # GENERATE A FULL ROW OF FEATURES
    dataset_segments, min_batch_size = train_test_validation_split(
        model_training,
        dataset,
        pipeline_components,
    )
    print(f'MIN BATCH SIZE:\t\t{min_batch_size}')

    # FREE UP MEMORY
    del dataset

    ########################################################################################
    ########################################################################################
    ### ADD SCALER

    # ADD FEATURE THAT CONVERTS FINAL DATAFRAME TO FLOAT MATRIX
    # OTHERWISE, THE SCALER WONT KNOW WHAT TO DO

    to_matrix_feature = feature_repo.create('to_feature_matrix', {
        'feature_columns': model_training['feature_columns']
    })
    pipeline_components.append(('hidden_ouput_conversion', to_matrix_feature))

    scaler_name = model_training['scaler']
    scaler_instance = scaler_repo.create(scaler_name)
    pipeline_components.append(('scaler', scaler_instance))

    ########################################################################################
    ########################################################################################
    ### ADD MODEL

    model_name = model_training['model']
    model_instance = model_repo.create(model_name)
    pipeline_components.append(('model', model_instance))

    ########################################################################################
    ########################################################################################
    ### TRAIN THE PIPELINE

    # CREATE THE PIPELINE
    pipeline = Pipeline(pipeline_components)

    # EXTRACT SEGMENT BLOCKS, THEN FREE UP MEMORY
    train_data = dataset_segments['train']
    test_data = dataset_segments['test']
    validate_data = dataset_segments['validate']
    del dataset_segments

    # TRAIN THE PIPELINE
    pipeline.fit(train_data.features, train_data.labels)

    # CHECK MODEL SCORE FOR EACH DATASET SEGMENT
    train_score = round(pipeline.score(train_data.features, train_data.labels), 4)
    test_score = round(pipeline.score(test_data.features, test_data.labels), 4)
    valid_score = round(pipeline.score(validate_data.features, validate_data.labels), 4)

    print('--------')
    print(f'TRAIN SCORE:\t\t{train_score}')
    print(f'TEST SCORE:\t\t{test_score}')
    print(f'VALIDATE SCORE:\t\t{valid_score}')
    print('--------')
    print(pipeline)

if __name__ == '__main__':
    run()

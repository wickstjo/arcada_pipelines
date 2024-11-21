from common import misc

from actions.data_retrieval.load_dataset import load_dataset
from actions.feature_engineering.to_dataframe.to_dataframe import to_dataframe
from actions.feature_engineering.shift_column.shift_column import shift_column
from actions.feature_engineering.stochastic_k.stochastic_k import stochastic_k
from actions.feature_engineering.to_feature_matrix.to_feature_matrix import to_feature_matrix
from actions.feature_engineering.drop_nan_rows.drop_nan_rows import drop_nan_rows

from actions.segmentation.segmentation import train_test_validation_split

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LinearRegression
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
    ### APPLY FEATURES

    available_features = {
        'shift_column': shift_column,
        'stochastic_k': stochastic_k,
    }

    # CONVERT INPUT TO DATAFRAME
    pipeline_components.append(('hidden_input_conversion', to_dataframe()))

    # ADD EACH CUSTOM FEATURE
    for nth, block in enumerate(experiment_config['feature_engineering']):
        feature_name = block['feature_name']
        feature_params = block['feature_params']

        feature_instance = available_features[feature_name](feature_params)
        pipeline_components.append((f'yaml_feature_{nth+1}', feature_instance))

    # DROP ALL ROWS WITH NAN VALUES
    pipeline_components.append(('hidden_cleanup', drop_nan_rows()))

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
    ### SCALER SELECTION

    # CONVERT DATAFRAME TO FLOAT MATRIX
    pipeline_components.append(('hidden_ouput_conversion', to_feature_matrix({
        'feature_columns': model_training['feature_columns']
    })))

    available_scalers = {
        'standard_scaler': StandardScaler,
        'minmax_scaler': MinMaxScaler
    }

    # ADD A SCALER
    scaler_name = model_training['scaler']
    assert scaler_name in available_scalers, f"SCALER '{scaler_name}' MISSING FROM SELECTION"
    pipeline_components.append(('standard_scaler', available_scalers[scaler_name]()))

    ########################################################################################
    ########################################################################################
    ### MODEL SELECTION

    # ADD A MODEL
    pipeline_components.append(('linreg_model', LinearRegression()))

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

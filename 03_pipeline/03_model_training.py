from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.constants as constants
import funcs.types as types
import machine_learning.options as ml_options
import funcs.misc as misc
import math, json, time

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT 
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # WHAT KAFKA TOPIC DO YOU WANT TO CONSUME DATA FROM?
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_TRAINING

        # WHAT ML MODEL SUITES ARE CURRENTLY AVAILABLE?
        self.model_options: dict = ml_options.IMPLEMENTED_MODELS()
        self.feature_options: dict = ml_options.IMPLEMENTED_FEATURES()

        # # ALL VALIDATION PASSES, FETCH MODEL CONFIG FROM YAML
        model_config: dict = misc.load_yaml('../00_configs/model_example.yaml')

        # CREATE MOCK EVENT
        self.on_kafka_event('MOCK_TOPIC', {
            'model_predecessor': False,
            'model_name': f'{int(time.time())}_my_cool_model',
            # 'model_name': 'my_cool_model',
            'model_config': json.dumps(model_config)
        })

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        training_request = misc.validate_dict(kafka_input, types.TRAINING_REQUEST)

        # PARSE JSON STRING TO DICT
        model_config: dict = json.loads(training_request['model_config'])

        # EXTRACT PROPS FOR READABILITY
        model_name: str = training_request['model_name']
        model_type: str = model_config['model_type']
        model_version: int = model_config['model_version']
        model_predecessor: int = training_request['model_predecessor']

        # EXTRACT PRE-PROCESSING CONFIGS
        dataset_config: dict = model_config['dataset']
        features_config: dict = model_config['feature_engineering']
        segmentation_config: dict = model_config['model_training']['data_segmentation']
        training_config: dict = model_config['model_training']

        ########################################################################################
        ########################################################################################

        # THROW ERROR IF THE REQUESTED MODEL TYPE HAS NOT BEEN IMPLEMENTED
        assert model_type in self.model_options, f"MODEL TYPE NOT AVAILABLE ({model_type})"
        
        # MAKE SURE THE MODEL NAME & VERSION IS UNIQUE
        count_query: str = f"SELECT COUNT(*) FROM {constants.cassandra.MODELS_TABLE} WHERE model_name = '{model_name}' AND model_version = {model_version} ALLOW FILTERING"
        db_matches: int = self.cassandra.count(count_query)
        assert db_matches == 0, 'A MODEL WITH THIS NAME & VERSION ALREADY EXISTS'

        ########################################################################################
        ########################################################################################

        # FETCH THE RAW DATASET FROM DB
        # APPLY FEATURES RECURSIVELY ON EACH DATASET ROW
        # SPLIT DATASET INTO TRAIN/TEST/VALIDATION SEGMENTS
        raw_dataset: list[dict] = self.fetch_dataset(dataset_config)
        feature_dataset: list[dict] = self.apply_features(raw_dataset, features_config)
        segmented_dataset: dict[str, list[dict]] = self.segment_dataset(feature_dataset, segmentation_config)

        ########################################################################################
        ########################################################################################

        misc.log(f'MODEL TRAINING ({model_type}) STARTED..')
        training_timer = misc.create_timer()
    
        # STITCH TOGETHER A UNIQUE FILENAME FOR THE MODEL
        model_filename: str = f"{model_type}::{model_name}::v{model_version}"

        # CREATE MODEL SUITE & START TRAINING
        model_suite = self.model_options[model_type]()
        model_suite.train_model(model_filename, segmented_dataset, training_config)

        delta_time: float = training_timer.stop()
        misc.log(f'MODEL TRAINING FINISHED IN {delta_time} SECONDS')

        ########################################################################################
        ########################################################################################

        # IF THE MODEL HAD A PREDECESSOR, RETIRE IT
        if model_predecessor:
            self.cassandra.query(f"UPDATE {constants.cassandra.MODELS_TABLE} SET active_status = False WHERE timestamp = '{training_request.predecessor}'")
            misc.log('RETIRED MODEL PREDECESSOR')

        # CONSTRUCT & VALIDATE NEW MODEL OBJECT
        new_model: dict = misc.validate_dict({
            'timestamp': int(training_timer.end_time),
            'model_name': model_name,
            'model_type': model_type,
            'model_version': model_version,
            'model_filename': model_filename,
            'active_status': True,
            'block_retraining': True,
            'model_config': json.dumps(model_config),
        }, types.MODEL_INFO)

        # PUSH MODEL DATA TO DB
        self.cassandra.write(constants.cassandra.MODELS_TABLE, new_model)
        misc.log('ACTIVATED NEWLY TRAINED MODEL')

    ########################################################################################
    ########################################################################################

    # ATTEMPT TO FETCH A N-SIZED DATASET
    # IF THERE ARENT ENOUGH ROWS YET, WAIT UNTIL THERE IS..
    def fetch_dataset(self, dataset_yaml: dict) -> list[dict]:

        # QUERY HOW MANY ROWS THE DATABASE HAS RIGHT NOW
        db_query: str = f"SELECT * FROM {dataset_yaml['db_table']} WHERE symbol = '{dataset_yaml['stock_symbol']}' ORDER BY {dataset_yaml['order_by']['column']} {dataset_yaml['order_by']['direction']} LIMIT {dataset_yaml['num_rows']}"
        dataset: list[dict] = self.cassandra.read(db_query, sort_by=dataset_yaml['order_by']['column'])

        # TERMINATE IF THERE ISNT ENOUGH DATA AVAILABLE
        assert len(dataset) == dataset_yaml['num_rows'], f"TABLE CONTAINS TOO FEW ROWS ({len(dataset)} < {dataset_yaml['num_rows']})"
        
        ### TODO: MAKE SURE ROWS MEET EXPECTED STRUCTURE
        ### TODO: MAKE SURE ROWS MEET EXPECTED STRUCTURE
        ### TODO: MAKE SURE ROWS MEET EXPECTED STRUCTURE

        misc.log(f"DATASET COLLECTED (n={dataset_yaml['num_rows']})")
        return dataset
    
    ########################################################################################
    ########################################################################################

    # APPLY ALL YAML FEATURES TO A DATASET
    def apply_features(self, dataset: list[dict], feature_yaml: dict) -> list[dict]:
        container: list[dict] = []

        # LOOP THROUGH EACH DATASET ROW
        for row in dataset:
            temp_row = row

            # RECURSIVELY APPLY EACH FEATURE, UPDATING TEMP ROW
            for item in feature_yaml['features']:
                for feature_name, feature_props in item.items():

                    # MAKE SURE THE FEATURE EXISTS
                    assert feature_name in self.feature_options, f"FEATURE '{feature_name}' DOES NOT EXIST"
                    
                    # APPLY IT
                    feature_suite = self.feature_options[feature_name]()
                    temp_row = feature_suite.apply(temp_row, feature_props)
                
            ### TODO: ADD EXPECTED OUTPUT VALIDATION
            ### TODO: ADD EXPECTED OUTPUT VALIDATION
            ### TODO: ADD EXPECTED OUTPUT VALIDATION

            # APPEND THE FINAL ROW VERSION TO THE NEW CONTAINER
            container.append(temp_row)

        misc.log(f"APPLIED FEATURES TO DATASET")
        return container

    ########################################################################################
    ########################################################################################

    def segment_dataset(self, dataset, segmentation) -> list[list[dict]]:
        total_length = len(dataset)
        container = {}
        start_index = 0
        
        # MAKE SURE THE COMBINED SEGMENTS ADD UP TO 100%
        total_percentage: int = sum(item[key] for item in segmentation for key in item)
        assert total_percentage == 100, f'YOUR SEGMENTS DO NOT ADD UP TO 100% ({total_percentage})'
        
        # LOOP THROUGH SEGMENTS -- IN ORDER
        for item in segmentation:
            for segment_name, segment_size in item.items():
                
                # FIGURE OUT SEGMENT SIZE
                segment_num_rows = math.ceil((segment_size/100) * total_length)
                end_index = (start_index + segment_num_rows) - 1
                misc.log(f'SEGMENTED ROWS ({start_index}-{end_index}, {segment_num_rows}) FOR {segment_name}')
                
                # ALLOCATE THE SUBSET & UPDATE NEXT STARTING INDEX
                container[segment_name] = dataset[start_index:end_index]
                start_index = end_index + 1
        
        return container

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
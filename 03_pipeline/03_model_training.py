from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.constants as constants
import funcs.types as types
import machine_learning.options as ml_options
import funcs.misc as misc
import math

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

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE REQUEST CONTAINS THE NECESSARY PARAMS
        training_request = misc.validate_dict(kafka_input, types.TRAINING_REQUEST, ns=True)

        # THROW ERROR IF THE REQUESTED MODEL TYPE IS NOT AVAILABLE
        if training_request.model_type not in self.model_options.keys():
            raise Exception(f'[REQUEST ERROR] MODEL TYPE NOT AVAILABLE ({training_request.model_type})')
        
        # STITCH TOGETHER A UNIQUE FILENAME FOR THE MODEL
        model_filename: str = f'{training_request.model_type}::{training_request.model_name}::v{training_request.model_version}'
        
        # CHECK DB IF A MODEL WITH THESE PARAMS ALREADY EXISTS
        count_query: str = f"SELECT COUNT(*) FROM {constants.cassandra.MODELS_TABLE} WHERE model_filename = '{model_filename}' ALLOW FILTERING"
        db_matches: int = self.cassandra.count(count_query)

        # IF IT DOES, TERMINATE..
        if db_matches > 0:
            raise Exception('[REQUEST ERROR] A MODEL WITH THESE PARAMS ALREADY EXISTS')

    ##########################################################################################################
    ##########################################################################################################

        # ALL VALIDATION PASSES, FETCH MODEL CONFIG FROM YAML
        model_config: dict = misc.load_yaml('../00_configs/model_example.yaml')

        # FETCH THE RAW DATASET FROM DB
        raw_dataset: list[dict] = self.fetch_dataset(
            model_config['dataset']
        )
        
        # APPLY FEATURES RECURSIVELY ON EACH DATASET ROW
        feature_dataset: list[dict] = self.apply_features(
            raw_dataset,
            model_config['feature_engineering']
        )

        # SPLIT DATASET INTO TRAIN/TEST/VALIDATION SEGMENTS
        segmented_dataset: dict = self.segment_dataset(
            feature_dataset,
            model_config['model_training']['data_segmentation']
        )

        return
    
    ##########################################################################################################
    ##########################################################################################################

        # # OTHERWISE, CREATE THE REQUESTED MODEL SUITE
        # # ATTEMPT TO LOAD ITS DATASET -- BLOCKING UNTIL DATABASE HAS ENOUGH ROWS
        # model_suite = self.model_options[training_request.model_type]()
        # dataset = self.fetch_dataset(model_suite.required_dataset_size)

        # misc.log(f'[MAIN] MODEL TRAINING STARTED ({training_request.model_type})..')
        # training_timer = misc.create_timer()

        # # INSTANTATE THE A MODEL SUITE & START TRAINING 
        # model_suite = self.model_options[training_request.model_type]()
        # model_suite.train_model(dataset, model_filename)

        # delta_time: float = training_timer.stop()
        # misc.log(f'[MAIN] MODEL TRAINING FINISHED IN {delta_time} SECONDS')

        # # IF THE MODEL HAD A PREDECESSOR, RETIRE IT
        # if training_request.predecessor:
        #     self.cassandra.query(f"UPDATE {constants.cassandra.MODELS_TABLE} SET active_status = False WHERE uuid = {training_request.predecessor}")
        #     misc.log('[MAIN] RETIRED MODEL PREDECESSOR')

        # # CONSTRUCT & VALIDATE NEW MODEL OBJECT
        # new_model: dict = misc.validate_dict({
        #     'uuid': misc.create_uuid(),
        #     'timestamp': int(training_timer.end_time),
        #     'model_name': training_request.model_name,
        #     'model_type': training_request.model_type,
        #     'model_version': training_request.model_version,
        #     'model_file': model_filename,
        #     'active_status': True,
        # }, types.MODEL_INFO)

        # # THEN PUSH IT TO KAFKA
        # self.cassandra.write(constants.cassandra.MODELS_TABLE, new_model)
        # misc.log('[MAIN] UPLOADED NEW MODEL')

    ########################################################################################
    ########################################################################################

    # ATTEMPT TO FETCH A N-SIZED DATASET
    # IF THERE ARENT ENOUGH ROWS YET, WAIT UNTIL THERE IS..
    def fetch_dataset(self, dataset_yaml: dict) -> list[dict]:

        # QUERY HOW MANY ROWS THE DATABASE HAS RIGHT NOW
        db_query: str = f"SELECT * FROM {dataset_yaml['db_table']} WHERE symbol = '{dataset_yaml['stock_symbol']}' ORDER BY {dataset_yaml['order_by']['column']} {dataset_yaml['order_by']['direction']} LIMIT {dataset_yaml['num_rows']}"
        dataset: list[dict] = self.cassandra.read(db_query, sort_by=dataset_yaml['order_by']['column'])

        # TERMINATE IF THERE ISNT ENOUGH DATA AVAILABLE
        if len(dataset) < dataset_yaml['num_rows']:
            raise Exception(f"[DATASET ERROR] TABLE CONTAINS TOO FEW ROWS ({len(dataset)} < {dataset_yaml['num_rows']})")
        
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

                    # THROW ERROR FOR MISSING FEATURES
                    if feature_name not in self.feature_options:
                        raise Exception(f'ERROR: FEATURE {feature_name} DOES NOT EXIST')
                    
                    try:
                        feature_suite = self.feature_options[feature_name]()
                        temp_row = feature_suite.apply(temp_row, feature_props)

                    except Exception as error:
                        misc.log(f'[FEATURE ERROR] ({feature_name}) {error}')
                
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
        total_percentage = sum(item[key] for item in segmentation for key in item)

        if total_percentage != 100:
            raise Exception(f'[SPLIT DATASET ERROR] YOUR SEGMENTS DO NOT ADD UP TO 100% ({total_percentage})')
        
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
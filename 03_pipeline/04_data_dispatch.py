from funcs.kafka_utils import create_kafka_producer, start_kafka_consumer
from funcs.cassandra_utils import create_cassandra_instance
import funcs.constants as constants
import funcs.types as types
import funcs.misc as misc
import funcs.thread_utils as thread_utils
import json

########################################################################################
########################################################################################

class create_pipeline_component:
    def __init__(self, process_beacon):

        # CREATE KAFKA PRODUCER & CASSANDRA CLIENT
        self.kafka_producer = create_kafka_producer()
        self.cassandra = create_cassandra_instance()

        # RELEVANT KAFKA TOPICS
        self.kafka_input_topics: str|list[str] = constants.kafka.MODEL_INFERENCE

        # CURRENTLY LOADED MODELS
        self.model_mutex = thread_utils.create_mutex()
        self.loaded_models: dict = {}

        # EVERY N SECONDS, CHECK CASSANDRA FOR MODEL CHANGES
        thread_utils.background_process(self.on_cassandra_event, 2, process_beacon)

    ########################################################################################
    ########################################################################################

    def on_cassandra_event(self):
    
        # CHECK DB FOR WHAT MODELS SHOULD CURRENTLY BE ACTIVE
        model_query: str = f"SELECT * FROM {constants.cassandra.MODELS_TABLE} WHERE active_status = True ALLOW FILTERING"
        query_result: list[dict] = self.cassandra.read(model_query)

        # CONVERT LIST OF DICTS TO DICT FORMAT
        db_models = {d['model_name']: d for d in query_result}

        # IF THERE ARE NO ACTIVE MODELS, MAKE SURE THERE ARE NO MODELS IN STATE
        if (len(db_models) == 0) and (len(self.loaded_models) > 0):
            for model_name in self.loaded_models:
                self.retire_model(model_name)
            return

        # COMPARE DB RESULTS TO MODEL STATE
        for model_name, model_info in db_models.items():

            # MODEL CANT BE FOUND IN STATE, ADD IT
            if model_name not in self.loaded_models:
                with self.model_mutex:
                    self.deploy_model(model_info)
                continue

            # OTHERWISE, THE MODEL IS LOADED
            # CHECK IF ITS A NEWER MODEL VERSION
            if model_info['model_version'] > self.loaded_models[model_name]['model_config']['model_version']:
                with self.model_mutex:

                    # RETIRE THE OLD MODEL & DEPLOY THE NEW ONE
                    self.retire_model(model_name)
                    self.deploy_model(model_info)
    
        # COMPARE MODEL STATE TO DB RESULTS
        for model_name in self.loaded_models:

            # MODEL FOUND IN STATE, BUT NO IN DB
            # THEREFORE, REMOVE MODEL
            if model_name not in db_models:
                with self.model_mutex:
                    self.retire_model(model_name)
        
    ########################################################################################
    ########################################################################################

    def deploy_model(self, model_info: dict):

        model_name = model_info['model_name']
        model_type = model_info['model_type']
        model_version = model_info['model_version']
        model_filename = model_info['model_filename']
        model_config = json.loads(model_info['model_config'])

        # MAKE SURE WE KNOW HOW TO DEAL WITH THE REQUESTED MODEL TYPE
        assert model_type in self.model_options, f'CANNOT PROCESS MODELS OF TYPE ({model_type})'

        # MAKE SURE WE DONT DOUBLE-LOAD THE SAME MODEL
        assert model_filename not in self.loaded_models, f'MODEL ALREADY LOADED ({model_filename})'

        # INSTANTIATE THE CORRECT MODEL SUITE & LOAD A MODEL FROM FILE
        model_suite = self.model_options[model_type]()
        model_suite.load_model(model_filename)

        # SAVE THE MODEL SUITE IN STATE FOR REPEATED USE
        self.loaded_models[model_name] = {
            'model_suite': model_suite,
            'model_config': model_config,
            'db_row': model_info,
        }

        misc.log(f"DEPLOYED MODEL '{model_name}' VERSION {model_version}")

    ########################################################################################
    ########################################################################################

    def retire_model(self, model_name: str):
        
        # MAKE SURE MODEL IS LOADED
        assert model_name in self.loaded_models, "MODEL '{model_name}' IS NOT CURRENTLY LOADED"
        model_version: int = self.loaded_models[model_name]['db_row']['model_version']

        misc.log(f"RETIRED MODEL '{model_name}' VERSION {model_version}")
        del self.loaded_models[model_name]

    ########################################################################################
    ########################################################################################

    # HANDLE INCOMING KAFKA EVENTS
    # THIS METHOD IS CALLED FOR EVERY EVENT
    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # MAKE SURE THE INPUT IS PROPER STOCK DATA
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)

        # DISABLE INFERENCE WHEN NO MODELS HAVE BEEN LOADED
        if len(self.loaded_models) == 0:
            misc.log('PAUSED: NO DEPLOYED MODELS YET')
            return

        # GENERATE A PREDICTION FOR EACH LOADED MODEL
        with self.model_mutex:
            model_predictions: dict = self.query_all_models(refined_stock_data)
            misc.log(f'GENERATED {len(model_predictions)} PREDICTIONS')

        # CREATE & VALIDATE PREDICTION BATCH
        prediction_batch: dict = misc.validate_dict({
            'input_row': refined_stock_data,
            'predictions': model_predictions
        }, types.PREDICTION_BATCH)

        # PUSH IT TO THE NEXT PIPELINE MODULE
        self.kafka_producer.push_msg(constants.kafka.DECISION_SYNTHESIS, prediction_batch)
        
        # FINALLY, RUN LIGHT PROBING METRICS FOR EACH MODEL
        with self.model_mutex:
            self.probe_all_models()

    ########################################################################################
    ########################################################################################

    def query_all_models(self, refined_input: dict) -> dict:
        predictions = {}
        
        # LOOP THROUGH MODELS
        for model_name, model_parts in self.loaded_models.items():

            # APPLY SAME FEATURES FROM MODEL TRAINING
            features_config = model_parts['model_config']['feature_engineering']
            input_with_features: dict = self.apply_features(refined_input, features_config)

            # PREDICT AN OUTCOME
            model_suite = model_parts['model_suite']
            predictions[model_name] = model_suite.predict_outcome(input_with_features)

        return predictions
    
    ########################################################################################
    ########################################################################################

    def apply_features(self, refined_input: dict, feature_yaml: dict) -> dict:
        temp_row = refined_input

        # RECURSIVELY APPLY EACH FEATURE, UPDATING TEMP ROW
        for item in feature_yaml['features']:
            for feature_name, feature_props in item.items():

                # MAKE SURE THE FEATURE EXISTS
                assert feature_name in self.feature_options, f"FEATURE '{feature_name}' DOES NOT EXIST"
                
                # APPLY IT
                feature_suite = self.feature_options[feature_name]()
                temp_row = feature_suite.apply(temp_row, feature_props)

        return temp_row
    
    ########################################################################################
    ########################################################################################

    def probe_all_models(self) -> dict:
        
        # LOOP THROUGH MODELS
        for model_name, model_parts in self.loaded_models.items():

            anomalies_detected = 0
            metrics_config = model_parts['model_config']['model_analysis']['light_metrics']

            # LOOP THROUGH METRICS
            for item in metrics_config['metrics']:
                for metric_name, metric_props in item.items():

                    # LOAD METRIC SUITE & MEASURE
                    metric_suite = self.metrics_options[metric_name]()
                    positive_result: bool = metric_suite.measure(metric_props)

                    # ANOMALOUS METRIC FOUND
                    if positive_result:
                        anomalies_detected += 1

                    # CHECK IF MINIMUM THRESHOLD HAS BEEN MET
                    if anomalies_detected >= metrics_config['quorum_threshold']:
                        self.kafka_producer.push_msg(constants.kafka.MODEL_ANALYSIS, model_parts['db_reference'])
                        misc.log(f'LIGHT PROBE QUORUM THRESHOLD MET ({model_name})')
                        return
                
            misc.log(f"RAN LIGHT PROBES FOR MODEL '{model_name}'")

########################################################################################
########################################################################################

start_kafka_consumer(create_pipeline_component)
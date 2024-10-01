from funcs import kafka_utils, redis_utils, mlflow_utils
from funcs import thread_utils, misc, constants, types

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, thread_beacon):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.redis = redis_utils.create_instance()
        self.mlflow = mlflow_utils.create_instance()

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.MODEL_DISPATCH, self.on_kafka_event, thread_beacon)
        self.redis.subscribe(constants.redis.MODEL_PIPELINES, self.on_redis_change, thread_beacon)
        self.mlflow.subscribe(self.on_mlflow_change, thread_beacon)

        # CURRENTLY DEPLOYED MODEL PIPES
        self.deployed_model_pipes = {}
        self.model_mutex = thread_utils.create_mutex()

        ### TODO: SPLIT PIPELINES AND MODEL STATES
        ### TODO: SPLIT PIPELINES AND MODEL STATES
        ### TODO: SPLIT PIPELINES AND MODEL STATES

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # VALIDATE INPUT
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)
        
        # MAKE SURE THE STOCK SYMBOL HAS MODEL PIPES DEPLOYED
        stock_symbol = refined_stock_data['symbol'].lower()
        assert stock_symbol in self.deployed_model_pipes, f"[COMPONENT] NO PIPES EXIST FOR STOCK SYMBOL '{stock_symbol}'"

        misc.log(f"[COMPONENT] RUNNING STOCK DATA ({stock_symbol}) THROUGH MODEL PIPES")

        # RESPONSE OBJECT
        prediction_batch = {
            'input_row': kafka_input,
            'predictions': {}
        }

        # IT DOES, SO LETS RUN THE INPUT ROW THROUGH EACH MODEL PIPE
        with self.model_mutex:
            for pipe_name, model_sequence in self.deployed_model_pipes[stock_symbol].items():
                # temp_value = refined_stock_data
                temp_value = 'input_row'

                misc.log(f"[COMPONENT] RUNNING PIPE '{pipe_name}'")

                # RECURSIVELY PREDICT WITH EACH MODEL
                # PREDECESSOR MODELS OUTPUT BECOMES SUCCESSOR MODELS INPUT
                for model in model_sequence:
                    temp_value = model.predict(temp_value)
                    misc.log(f"[COMPONENT] PREDICTED WITH MODEL '{model.model_name}'")

                # SAVE THE FINAL OUTPUT VALUE AS THE PIPES RESULT
                prediction_batch['predictions'][pipe_name] = temp_value

        # MAKE SURE THE VALIDATION BLOCK LOOKS OK
        # THEN PUSH IT BACK INTO KAFKA
        valid_prediction_batch: dict = misc.validate_dict(prediction_batch, types.PREDICTION_BATCH)
        self.kafka.push(constants.kafka.DECISION_SYNTHESIS, valid_prediction_batch)

    ########################################################################################
    ########################################################################################

    def on_mlflow_change(self, latest_models: dict):
        misc.log('[COMPONENT] MLFLOW MODEL VERSIONS HAVE CHANGED')

        # LOOP THROUGH EACH MODEL PIPE
        for stock_symbol, stock_pipes in self.deployed_model_pipes.items():
            for pipe_name, model_sequence in stock_pipes.items():
                for nth_model, model in enumerate(model_sequence):
                    pass

    ########################################################################################
    ########################################################################################

    def on_redis_change(self, latest_pipelines: dict):
        assert isinstance(latest_pipelines, dict), '[COMPONENT] REDIS VALUE WAS NOT A DICT'
        misc.log('[COMPONENT] MODEL PIPES HAVE CHANGED')

        # LATER: FETCH UPDATED LIST OF MLFLOW MODELS
        model_versions = self.mlflow.list_all_models()

        # CONSTRUCT MODEL PIPELINES FROM JSON DATA
        with self.model_mutex:
            for stock_symbol, stock_pipes in latest_pipelines.items():
                pipes = {}

                for pipe_name, model_sequence in stock_pipes.items():
                    models = []

                    # CONSTRUCT REQUESTED MODEL
                    for block in model_sequence:
                        model_name = block['model_name']
                        version_alias = block['version_alias']

                        # MAKE SURE MODEL EXISTS
                        if model_name not in model_versions:
                            misc.log(f"[COMPONENT] MODEL '{model_name}' DOES NOT EXIST")
                            continue

                        # MAKE SURE MODEL VERSION ALIAS EXISTS
                        if version_alias not in model_versions[model_name]:
                            misc.log(f"[COMPONENT] MODEL ALIAS '{version_alias}' DOES NOT EXIST")
                            continue

                        # FIND THE VERSION ALIAS' NUMERIC REPRESENTATION
                        version_num = model_versions[model_name][version_alias]

                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED?
                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED?
                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED?

                        # LOAD IN FAKE MODELS -- FOR TESTING
                        model = self.mlflow.load_fake_model(model_name, version_alias, version_num)
                        models.append(model)

                    pipes[pipe_name] = models
                self.deployed_model_pipes[stock_symbol] = pipes

        misc.log('[COMPONENT] FINISHED APPLYING PIPELINE CHANGES')
        
########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
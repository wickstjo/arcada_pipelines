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

        ### TODO: SUBSCRIBE TO MLFLOW MODEL CHANGES
        ### TODO: SUBSCRIBE TO MLFLOW MODEL CHANGES
        ### TODO: SUBSCRIBE TO MLFLOW MODEL CHANGES

        # CURRENTLY DEPLOYED MODEL PIPES
        self.deployed_model_pipes = {}
        self.model_mutex = thread_utils.create_mutex()

        ### TODO: SPLIT PIPELINES AND MODEL STATES?
        ### TODO: SPLIT PIPELINES AND MODEL STATES?
        ### TODO: SPLIT PIPELINES AND MODEL STATES?

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):

        # VALIDATE INPUT
        refined_stock_data: dict = misc.validate_dict(kafka_input, types.REFINED_STOCK_DATA)
        
        # MAKE SURE THE STOCK SYMBOL HAS MODEL PIPES DEPLOYED
        stock_symbol = refined_stock_data['symbol'].lower()
        assert stock_symbol in self.deployed_model_pipes, f"[KAFKA CALLBACK] NO PIPES EXIST FOR STOCK SYMBOL '{stock_symbol}'"

        misc.log(f"[KAFKA CALLBACK] RUNNING STOCK DATA ({stock_symbol}) THROUGH MODEL PIPES")

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

                misc.log(f"[KAFKA CALLBACK] RUNNING PIPE '{pipe_name}'")

                # RECURSIVELY PREDICT WITH EACH MODEL
                # PREDECESSOR MODELS OUTPUT BECOMES SUCCESSOR MODELS INPUT
                for model in model_sequence:
                    temp_value = model.predict(temp_value)
                    misc.log(f"[KAFKA CALLBACK] PREDICTED WITH MODEL '{model.model_name}'")

                # SAVE THE FINAL OUTPUT VALUE AS THE PIPES RESULT
                prediction_batch['predictions'][pipe_name] = temp_value

        # MAKE SURE THE VALIDATION BLOCK LOOKS OK
        # THEN PUSH IT BACK INTO KAFKA
        valid_prediction_batch: dict = misc.validate_dict(prediction_batch, types.PREDICTION_BATCH)
        self.kafka.push(constants.kafka.DECISION_SYNTHESIS, valid_prediction_batch)

    ########################################################################################
    ########################################################################################

    def on_redis_change(self, latest_value: dict):
        assert isinstance(latest_value, dict), '[REDIS CALLBACK] REDIS VALUE WAS NOT A DICT'
        misc.log('[REDIS CALLBACK] MODEL PIPES HAVE CHANGED')

        # LATER: FETCH UPDATED LIST OF MLFLOW MODELS
        # model_versions = self.mlflow.list_all_models()

        # CONSTRUCT MODEL PIPELINES FROM JSON DATA
        with self.model_mutex:
            for stock_symbol, stock_pipes in latest_value.items():
                pipes = {}

                for pipe_name, model_sequence in stock_pipes.items():
                    models = []

                    # CONSTRUCT REQUESTED MODEL
                    for block in model_sequence:
                        model_name = block['model']
                        model_version = block['version']

                        ### TODO: CHECK IF MODEL EXISTS
                        ### TODO: CHECK IF MODEL EXISTS
                        ### TODO: CHECK IF MODEL EXISTS

                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED
                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED
                        ### TODO: CHECK IF THE SAME MODEL IS ALREADY DEPLOYED

                        # LOAD IN FAKE MODELS -- FOR TESTING
                        model = self.mlflow.load_fake_model(model_name, model_version)
                        models.append(model)

                    pipes[pipe_name] = models
                self.deployed_model_pipes[stock_symbol] = pipes

        misc.log('[REDIS CALLBACK] FINISHED APPLYING MODEL PIPE CHANGES')
        
########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
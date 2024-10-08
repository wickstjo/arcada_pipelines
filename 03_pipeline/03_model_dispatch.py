from funcs import kafka_utils, redis_utils, mlflow_utils, jaeger_utils
from funcs import thread_utils, misc, constants, types

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.redis = redis_utils.create_instance()
        self.mlflow = mlflow_utils.create_instance()
        self.jaeger = jaeger_utils.create_instance('MODEL_DISPATCH')

        # IN A BACKGROUND THREAD, DO...
        self.kafka.subscribe(constants.kafka.MODEL_DISPATCH, self.on_kafka_event, structs.thread_beacon)
        self.redis.subscribe(constants.redis.MODEL_PIPELINES, self.on_redis_change, structs.thread_beacon)
        # self.mlflow.subscribe(self.on_mlflow_change, structs.thread_beacon)

        # MOCK MLFLOW VERSION API
        self.mock_version_repo: str = 'model_versions'
        self.redis.subscribe(self.mock_version_repo, self.on_mlflow_change, structs.thread_beacon)

        # CURRENTLY DEPLOYED MODEL PIPES
        self.deployed_model_pipes = {}
        self.model_mutex = thread_utils.create_mutex()

    ########################################################################################
    ########################################################################################

    def on_kafka_event(self, kafka_topic: str, kafka_input: dict):
        try:
            assert 'trace' in kafka_input, "[INFERENCE] EVENT MISSING 'trace' PROPERTY"
            assert 'refined_stock_data' in kafka_input, "[INFERENCE] EVENT MISSING 'refined_stock_data' PROPERTY"

            trace_precedessor = kafka_input['trace']
            refined_stock_data = kafka_input['refined_stock_data']

            # FORCE STOCK SYMBOL TO LOWERCASE TO AVOID CAPITALIZATION ACCIDENTS
            # MAKE SURE AT LEAST ONE PIPE EXISTS
            stock_symbol = refined_stock_data['symbol'].lower()
            assert stock_symbol in self.deployed_model_pipes, f"[INFERENCE] NO PIPES EXIST FOR STOCK SYMBOL '{stock_symbol}'"

            # THREAD-SAFE VALUE CONTAINER
            prediction_batch = thread_utils.kv_list()

            # BLOCK MODEL STATE MODIFICATIONS DURING INFERENCE
            with self.model_mutex:
                threads = []

                # LOOP THROUGH EACH REGISTERED MODEL PIPE
                for pipe_props in self.deployed_model_pipes[stock_symbol].items():

                    def func(target_pipe):
                        pipe_name, model_sequence = target_pipe
                        local_predecessor = trace_precedessor

                        # temp_value = refined_stock_data
                        temp_value = 'init_value'

                        # RECURSIVELY PREDICT WITH EACH MODEL
                        # PREDECESSOR MODELS OUTPUT BECOMES SUCCESSOR MODELS INPUT
                        for model in model_sequence:
                            with self.jaeger.create_span(f"PREDICTING WITH '{stock_symbol}.{pipe_name}.{model.model_name}'", local_predecessor) as span:
                                temp_value = model.predict(temp_value)
                                local_predecessor = span

                        # SAVE THE FINAL OUTPUT VALUE AS THE PIPES RESULT
                        prediction_batch.add(pipe_name, temp_value, local_predecessor)

                    # RUN EACH PIPE IN A SEPARATE THREAD
                    thread = thread_utils.start_thread(func, (pipe_props,))
                    threads.append(thread)
                
                # WAIT FOR ALL THREADS TO FINISH
                [thread.join() for thread in threads]

            # EVERY PIPE IS DONE
            # PUSH PREDICTION BATCH TO DECISION SYNTHESIS
            with self.jaeger.create_span("KAFKA: FORWARDING PREDICTION BATCH", prediction_batch.last_pipe) as span:
                self.kafka.push(constants.kafka.DECISION_SYNTHESIS, {
                    'trace': self.jaeger.create_context(span),
                    'prediction_batch': {
                        'input_row': refined_stock_data,
                        'pipe_predictions': prediction_batch.container
                    }
                })

        except AssertionError as error:
            misc.log(error)

    ########################################################################################
    ########################################################################################

    def on_mlflow_change(self, latest_model_versions: dict):
        try:
            assert isinstance(latest_model_versions, dict), '[MODEL STATE] REDIS VALUE WAS NOT A DICT'
            misc.log('[MODEL STATE] MLFLOW MODEL VERSIONS HAVE CHANGED')

            # LOOP THROUGH EACH MODEL PIPE
            for stock_symbol, stock_pipes in self.deployed_model_pipes.items():
                for pipe_name, model_sequence in stock_pipes.items():
                    for nth_model, model in enumerate(model_sequence):

                        # MAKE SURE THE MODEL STILL EXISTS
                        assert model.model_name in latest_model_versions, f"[MODEL STATE] MODEL '{model.model_name}' NO LONGER EXISTS"

                        ### TODO: ON ASSERT FAIL, THE PIPE IS BROKEN
                        ### TODO: ON ASSERT FAIL, THE PIPE IS BROKEN

                        # IF THE DEPLOYED MODEL IS BOUND TO A VERSION ALIAS
                        # MAKE SURE THAT THE VERSION STILL MATCHES
                        if model.version_alias:
                            
                            # MAKE SURE THE ALIAS STILL EXISTS
                            assert model.version_alias in latest_model_versions[model.model_name], f"[MODEL STATE] VERSION ALIAS '{model.version_alias}' NO LONGER EXISTS FOR MODEL '{model.model_name}'"
                            
                            ### TODO: ON ASSERT FAIL, THE PIPE IS BROKEN
                            ### TODO: ON ASSERT FAIL, THE PIPE IS BROKEN

                            old_version = model.version_number
                            newest_version = latest_model_versions[model.model_name][model.version_alias]

                            # VERSION HAS CHANGED, SO UPDATE MODEL IN PIPELINE STATE
                            if old_version != newest_version:
                                with self.model_mutex:

                                    # USING FAKE MODEL FOR TESTING
                                    new_model = self.mlflow.load_fake_model(model.model_name, model.version_alias, newest_version)
                                    self.deployed_model_pipes[stock_symbol][pipe_name][nth_model] = new_model

                                misc.log(f"[MODEL STATE] UPDATED MODEL '{model.model_name}' VERSION ({old_version} -> {newest_version}) IN PIPE '{pipe_name}'")

                        # OTHERWISE, VERIFY THAT THE NUMERIC VERSION STILL EXISTS
                        # else:
                        #     assert self.mlflow.model_exists(model.model_name, model.version_number), f"[MODEL STATE] MODEL '{model.model_name}' VERSION {model.version_number} NO LONGER EXISTS"

            misc.log('[MODEL STATE] UPDATED PIPELINE STATE (MLFLOW)')

        except AssertionError as error:
            misc.log(error)
            misc.log('[MODEL STATE] REVERTED PIPELINE STATE UPDATE (MLFLOW)')

    ########################################################################################
    ########################################################################################

    def on_redis_change(self, latest_model_pipelines: dict):
        try:
            assert isinstance(latest_model_pipelines, dict), '[PIPELINE STATE] REDIS VALUE WAS NOT A DICT'
            misc.log('[PIPELINE STATE] MODEL PIPES HAVE CHANGED')

            # LATER: FETCH UPDATED LIST OF MLFLOW MODELS
            # latest_model_versions = self.mlflow.list_all_models()
            latest_model_versions = self.redis.get(self.mock_version_repo)

            # CONSTRUCT MODEL PIPELINES FROM JSON DATA
            for stock_symbol, stock_pipes in latest_model_pipelines.items():
                pipes = {}

                for pipe_name, model_sequence in stock_pipes.items():
                    models = []

                    misc.log(f"[PIPELINE STATE] DEPLOYING PIPE '{pipe_name}' FOR STOCK '{stock_symbol}'")

                    # CONSTRUCT REQUESTED MODEL
                    for block in model_sequence:
                        assert 'model_name' in block, f"[PIPELINE STATE] MODEL PROPERTY 'model_name' MISSING"
                        assert 'model_version' in block, f"[PIPELINE STATE] MODEL PROPERTY 'model_version' MISSING"

                        model_name = block['model_name']
                        version_number = block['model_version']
                        version_alias = None

                        # MAKE SURE MODEL EXISTS IN MLFLOW
                        assert model_name in latest_model_versions, f"[PIPELINE STATE] MODEL '{model_name}' DOES NOT EXIST"

                        # AUDIT -- IF A STRINGIFIED VERSION ALIAS WAS PROVIDED
                        if type(version_number) == str:
                            assert version_number in latest_model_versions[model_name], f"[PIPELINE STATE] MODEL ALIAS '{version_number}' DOES NOT EXIST FOR MODEL '{model_name}'"

                            # ALIAS EXISTS, UPDATE VERSION PROPS
                            version_alias = version_number
                            version_number = latest_model_versions[model_name][version_alias]

                        # MAKE SURE MODEL VERSION STILL EXISTS
                        # assert self.mlflow.model_exists(model_name, version_number), f"[PIPELINE CHANGE] MODEL '{model_name}' VERSION {version_number} DOES NOT EXISTS"

                        # LOAD IN FAKE MODELS -- FOR TESTING
                        model = self.mlflow.load_fake_model(model_name, version_alias, version_number)
                        models.append(model)
                        misc.log(f'[PIPELINE STATE] DEPLOYED MODEL {model_name, version_alias, version_number}')

                    # FINISHED ONE PIPE
                    pipes[pipe_name] = models

                # FINISHED ALL PIPES FOR STOCK
                with self.model_mutex:
                    self.deployed_model_pipes[stock_symbol] = pipes

            misc.log('[PIPELINE STATE] UPDATED PIPELINE STATE (REDIS)')

        except AssertionError as error:
            misc.log(error)
            misc.log('[PIPELINE STATE] REVERTED PIPELINE STATE UPDATE (REDIS)')
        
########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
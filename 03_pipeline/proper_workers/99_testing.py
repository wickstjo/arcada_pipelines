from funcs import kafka_utils, redis_utils, mlflow_utils
from funcs import thread_utils, misc, constants, types

########################################################################################
########################################################################################

class pipeline_component:
    def __init__(self, structs):

        # CREATE INSTANCED CLIENTS
        self.kafka = kafka_utils.create_instance()
        self.redis = redis_utils.create_instance()
        self.mlflow = mlflow_utils.create_instance()

        # self.mlflow.load_model('foo', 2)
        model_versions = self.mlflow.list_all_models()
        print(model_versions)

########################################################################################
########################################################################################

thread_utils.start_coordinator(pipeline_component)
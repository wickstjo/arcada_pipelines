# !pip install mlflow
import mlflow
from mlflow.tracking import MlflowClient
from funcs import constants, mock

global_config = constants.global_config()
MLFLOW_BROKER: str = f"http://{global_config.cluster.mlflow_broker}"

########################################################################################################
########################################################################################################

class create_instance:
    def __init__(self):
        
        # POINT REGISTRY & MODEL TRACKING TOWARDS THE CLUSTER BROKER
        mlflow.set_tracking_uri(MLFLOW_BROKER)
        mlflow.set_registry_uri(MLFLOW_BROKER)

        # CREATE A REUSABLE CLIENT
        self.instance = MlflowClient()

    ########################################################################################################
    ########################################################################################################

    def list_all_models(self):
        container = {}
        
        for item in self.instance.search_registered_models():
            version_data = item.__dict__['_latest_version']
            assert len(version_data) == 1, '[MLFLOW] THERE IS AN ABNORMAL NUMBER OF MODEL VERSIONS'
            
            container[item._name] = {
                'latest_version': version_data[0].version,
                'version_aliases': item.aliases
            }
    
        return container

    ########################################################################################################
    ########################################################################################################

    def load_model(self, model_name: str, model_version: int):
        assert isinstance(model_name, str), 'MODEL NAME MUST BE OF TYPE STR'
        assert isinstance(model_version, int), 'MODEL VERSION MUST BE OF TYPE INT'
        
        model_uri = f'models:/{model_name}/{model_version}' 
        model = mlflow.pyfunc.load_model(model_uri)

        return model

    ########################################################################################################
    ########################################################################################################

    def load_fake_model(self, model_name: str, model_version: int|str):
        return mock.ml_model(model_name, model_version)
    
########################################################################################################
########################################################################################################
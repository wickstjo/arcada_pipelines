from fastapi import APIRouter, Response, status
import funcs.constants as constants
import mlflow
from mlflow.tracking import MlflowClient

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = constants.global_config()

# POINT MLFLOW AT THE CLUSTER ENDPOINT
mlflow.set_tracking_uri(f'http://{global_config.cluster.mlflow_broker}')
mlflow.set_registry_uri(f'http://{global_config.cluster.mlflow_broker}')

########################################################################################################
########################################################################################################

@router.get('/mlflow/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        client = MlflowClient()
        
        return client.search_registered_models()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'[MLFLOW ROOT ERROR] {error}'

########################################################################################################
########################################################################################################
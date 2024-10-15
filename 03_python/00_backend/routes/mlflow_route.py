from fastapi import APIRouter, Response, status
from mlflow.tracking import MlflowClient
import mlflow
import common.constants as constants

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = constants.global_config()
MLFLOW_BROKER: str = f"http://{global_config.endpoints.host}:{global_config.endpoints.ports.mlflow}"

# POINT MLFLOW AT THE CLUSTER ENDPOINT
mlflow.set_tracking_uri(MLFLOW_BROKER)
mlflow.set_registry_uri(MLFLOW_BROKER)

instance = MlflowClient()

########################################################################################################
########################################################################################################

@router.get('/mlflow/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return instance.search_registered_models()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'[MLFLOW ROOT ERROR] {error}'

########################################################################################################
########################################################################################################
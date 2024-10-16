from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from common import mlflow_utils

########################################################################################################
########################################################################################################

router = APIRouter()
mlflow = mlflow_utils.create_instance()

########################################################################################################
########################################################################################################

@router.get('/mlflow/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return mlflow.instance.search_registered_models()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'domain': 'MLFLOW LISTING',
            'error': error
        }

########################################################################################################
########################################################################################################

class USE_MODEL(BaseModel):
    model_name: str
    model_version: int
    model_input: dict

@router.post('/mlflow/inference')
async def foo(request: USE_MODEL, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        
        # ATTEMPT TO LOAD THE MODEL, THEN PREDICT WITH IT
        model = mlflow.load_model(request.model_name, request.model_version)
        prediction = model.predict(request.model_input)

        return {
            'request': request,
            'model_prediction': prediction
        }
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'domain': 'MLFLOW INFERENCE',
            'error': error
        }

########################################################################################################
########################################################################################################

@router.get('/mlflow/{model_name}/{model_version}')
async def foo(model_name: str, model_version: int, response: Response):
    try:
        response.status_code = status.HTTP_200_OK

        # EXTRACT MODEL INFO & TRACE ITS RUN PARAMS
        model_info = mlflow.model_info(model_name, model_version)
        run_info = mlflow.run_info(model_info._run_id)

        return {
            'model_info': model_info,
            'run_info': run_info
        }

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            'domain': 'MLFLOW MODEL INFO',
            'error': error
        }

########################################################################################################
########################################################################################################
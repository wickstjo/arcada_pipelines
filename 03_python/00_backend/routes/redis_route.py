from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from common import constants, redis_utils

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = constants.global_config()
redis = redis_utils.create_instance()

########################################################################################################
########################################################################################################

@router.get('/redis/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        container = {}

        for key in redis.instance.keys('*'):
            stringified_key: str = key.decode('utf-8')
            container[key] = redis.get(stringified_key)

        return container

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'[REDIS ERROR] {error}'

########################################################################################################
########################################################################################################

class KeyValue(BaseModel):
    key: str
    value: int|float|str|dict

@router.post('/redis/create')
async def foo(kv: KeyValue, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        redis.set(kv.key, kv.value)

        return {
            kv.key: kv.value
        }
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error
    
########################################################################################################
########################################################################################################

@router.get('/redis/{key_name}')
async def foo(key_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        
        if redis.exists(key_name):
            return redis.get(key_name)
        
        return f"ERROR: REDIS KEY '{key_name}' IS NOT SET"
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error
    
########################################################################################################
########################################################################################################
from fastapi import APIRouter, Response, status
from funcs import constants, redis_utils

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
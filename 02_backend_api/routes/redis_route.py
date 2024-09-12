from fastapi import APIRouter, Response, status
import funcs.misc as misc
import redis

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = misc.load_global_config()
redis_host, redis_port = global_config.cluster.redis_broker.split(':')
redis_instance = redis.StrictRedis(host=redis_host, port=int(redis_port), db=0)

########################################################################################################
########################################################################################################

@router.get('/redis/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        container = {}

        # CRAWL THROUGH REDIS KEYSTORE
        for key in redis_instance.keys('*'):
            container[key] = redis_instance.get(key)

        return container

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'REDIS ROOT ERROR: {str(error)}'

########################################################################################################
########################################################################################################

# @router.get('/redis/init')
# async def initialize_default_content(response: Response):
#     try:
#         # CREATE DEFAULT KEYSTORE
#         response.status_code = status.HTTP_201_CREATED
#         redis_instance.mset(global_config.backend.create_on_init.redis_keystore.__dict__)

#         return global_config.backend.create_on_init.redis_keystore
    
#     except Exception as error:
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return f'REDIS INIT ERROR: {str(error)}'

########################################################################################################
########################################################################################################

@router.get('/redis/{key_name}')
async def keystore(key_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        key_value = redis_instance.get(key_name)

        # NOT FOUND, THROW ERROR
        if not key_value:
            response.status_code = status.HTTP_404_NOT_FOUND
            return None
        
        # FOUND
        return key_value

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'REDIS KEYSTORE ERROR: {str(error)}'
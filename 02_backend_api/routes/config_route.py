from fastapi import APIRouter, Response, status
import funcs.constants as constants

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = constants.global_config()

########################################################################################################
########################################################################################################

@router.get('/global_config/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return global_config

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'[GLOBAL CONFIG ERROR]: {error}'

########################################################################################################
########################################################################################################
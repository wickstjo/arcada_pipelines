from fastapi import APIRouter, Response, status
import funcs.misc as misc

########################################################################################################
########################################################################################################

router = APIRouter()
global_config = misc.load_global_config()

########################################################################################################
########################################################################################################

@router.get('/config/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return global_config

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'PIPELINE CONFIG ROOT ERROR: {str(error)}'

########################################################################################################
########################################################################################################
from fastapi import APIRouter, Response, status
router = APIRouter()

@router.get('/actions/')
async def read_users(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return [
        {'username': 'Rick'}, 
        {'username': 'Morty'}
    ]

@router.get('/actions/{action_name}')
async def read_user(action_name: str, response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {
        'actions': action_name
    }

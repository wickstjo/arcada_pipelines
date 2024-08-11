from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import utils.cassandra as cassandra_utils

########################################################################################################
########################################################################################################

router = APIRouter()

########################################################################################################
########################################################################################################

@router.get('/cassandra/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return []

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################

@router.get('/cassandra/{table_name}')
async def table_details(table_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return {
            'n_rows': 4,
            'head': [
                'foo',
                'bar'
            ],
            'tail': [
                'biz',
                'baz'
            ],
        }

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################

class Table(BaseModel):
    name: str
    num_partitions: int

@router.post('/cassandra/create')
async def create_table(table: Table, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        # TODO CREATE TABLE

        return {
            'topic_name': table.name,
            'num_partitions': table.num_partitions
        }
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################
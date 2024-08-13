from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import utils.cassandra as cassandra_utils

########################################################################################################
########################################################################################################

router = APIRouter()
cassandra = cassandra_utils.create_cassandra_instance()

########################################################################################################
########################################################################################################

@router.get('/cassandra/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.db_overview()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################

class Table(BaseModel):
    domain: str
    columns: dict
    indexing: list

@router.post('/cassandra/create')
async def create_table(table: Table, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        cassandra.create_table(table.domain, table.columns, table.indexing)
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################

@router.get('/cassandra/{keyspace_name}')
async def overview(keyspace_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.keyspace_overview(keyspace_name)

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)
    
########################################################################################################
########################################################################################################

@router.get('/cassandra/{keyspace_name}/{table_name}')
async def overview(keyspace_name: str, table_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.table_overview(keyspace_name, table_name)

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)
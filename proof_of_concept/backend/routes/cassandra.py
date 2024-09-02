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

# CREATE DEFAULT TABLES AFTER A FRESH DOCKER LAUNCH
@router.get('/cassandra/init')
async def init_experiment_topics(response: Response):

    try:
        response.status_code = status.HTTP_201_CREATED

        # TABLE FOR STOCK DATA
        cassandra.create_table('testing_keyspace.testing_table', {
            'timestamp': 'int',
            'open': 'float',
            'close': 'float',
            'high': 'float',
            'low': 'float',
            'volume': 'int',
        }, ['timestamp'])
    
        return "DOMAIN 'testing_keyspace.testing_table' CREATED"

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)

########################################################################################################
########################################################################################################

@router.get('/cassandra/{keyspace_name}')
async def keyspace_overview(keyspace_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.keyspace_overview(keyspace_name)

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)
    
########################################################################################################
########################################################################################################

@router.get('/cassandra/{keyspace_name}/{table_name}')
async def table_overview(keyspace_name: str, table_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return 'TODO'
        #return cassandra.table_overview(keyspace_name, table_name)

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return 'ERROR: ' + str(error)
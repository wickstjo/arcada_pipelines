from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import funcs.cassandra_utils as cassandra_utils
import funcs.misc as misc

########################################################################################################
########################################################################################################

router = APIRouter()
cassandra = cassandra_utils.create_cassandra_instance()
global_config = misc.load_global_config()

########################################################################################################
########################################################################################################

@router.get('/cassandra/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.db_overview()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'CASSANDRA ROOT ERROR: {str(error)}'

########################################################################################################
########################################################################################################

class CREATE_TABLE(BaseModel):
    keyspace_name: str
    table_name: str
    columns: dict
    indexing: list

@router.post('/cassandra/create')
async def create_table(table: CREATE_TABLE, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        cassandra.create_table(table.keyspace_name, table.table_name, table.columns, table.indexing)
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'CASSANDRA CREATE ERROR: {str(error)}'

########################################################################################################
########################################################################################################

class DROP_TABLE(BaseModel):
    keyspace_name: str
    table_name: str

@router.post('/cassandra/drop')
async def create_table(table: DROP_TABLE, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        cassandra.drop_table(table.keyspace_name, table.table_name)
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'CASSANDRA DROP ERROR: {str(error)}'

########################################################################################################
########################################################################################################

# CREATE DEFAULT TABLES AFTER A FRESH DOCKER LAUNCH
@router.get('/cassandra/init')
async def initialize_default_content(response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        container = []

        # FETCH WHAT TABLES TO CREATE FROM THE GLOBAL CONFIG
        cassandra_tables = global_config.backend.create_on_init.cassandra_tables

        # CREATE EACH LISTED TABLE
        for item in cassandra_tables:
            try:
                cassandra.create_table(item.keyspace, item.table_name, item.columns.__dict__, item.primary_keys)
                container.append(f"TABLE '{item.keyspace}.{item.table_name}' CREATED")
            except Exception as error:
                container.append(f"'{item.keyspace}.{item.table_name}': {str(error)}")

        return container

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return F'CASSANDRA INIT ERROR: {str(error)}'

########################################################################################################
########################################################################################################

@router.get('/cassandra/{keyspace_name}')
async def keyspace_overview(keyspace_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return cassandra.keyspace_overview(keyspace_name)

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'CASSANDRA KEYSPACE ERROR: {str(error)}'
    
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
        return f'CASSANDRA FETCH ERROR: {str(error)}'
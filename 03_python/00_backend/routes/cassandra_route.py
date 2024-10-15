from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from common import cassandra_utils, constants

########################################################################################################
########################################################################################################

router = APIRouter()
cassandra = cassandra_utils.create_instance()
global_config = constants.global_config()

# WHAT CASSANDRA TABLES ARE ONLY EXIST FOR MAINTENANCE
CASSANDRA_AUXILLARY_TABLES = ['system_auth', 'system_schema', 'system_distributed', 'system', 'system_traces']

########################################################################################################
########################################################################################################

@router.get('/cassandra/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        container = {}
        
        # QUERY ALL EXISTING TABLES
        all_tables: list[dict] = cassandra.read(f"SELECT keyspace_name, table_name FROM system_schema.tables")

        # LOOP THROUGH THEM
        for item in all_tables:
            keyspace = item['keyspace_name']
            table= item['table_name']

            # HIDE AUXILLARY TABLES
            if (global_config.backend.hide_auxillary) and (keyspace in CASSANDRA_AUXILLARY_TABLES):
                continue

            # ADD KEYSPACE TO RESPONSE
            if keyspace not in container:
                container[keyspace] = []

            # ADD TABLE TO RESPONSE
            container[keyspace].append(table)

        return container

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error

########################################################################################################
########################################################################################################

class CREATE_TABLE(BaseModel):
    keyspace_name: str
    table_name: str
    columns: dict
    indexing: list

@router.post('/cassandra/create')
async def foo(table: CREATE_TABLE, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        cassandra.create_table(table.keyspace_name, table.table_name, table.columns, table.indexing)

        return table
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error

########################################################################################################
########################################################################################################

class DROP_TABLE(BaseModel):
    keyspace_name: str
    table_name: str

@router.post('/cassandra/drop')
async def foo(table: DROP_TABLE, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        cassandra.drop_table(table.keyspace_name, table.table_name)
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error

########################################################################################################
########################################################################################################

# OVERVIEW OF KEYSPACE TABLES
@router.get('/cassandra/{keyspace_name}')
async def foo(keyspace_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        container = {}
        
        # CHECK CONTENTS OF KEYSPACE
        keyspace_content = cassandra.read(f"SELECT * FROM system_schema.columns WHERE keyspace_name= '{keyspace_name}'")

        # STOP IF THE KEYSPACE IS EMPTY
        if len(keyspace_content) == 0:
            return 'KEYSPACE IS EMPTY OR DOES NOT EXIST'
        
        # LOOP IN TABLE STRUCTURES
        for row in keyspace_content:

            # CREATE TABLE KEY IF IT DOESNT EXIST
            if row['table_name'] not in container:
                container[row['table_name']] = {
                    'n_rows': None,
                    'columns': {},
                    'indexing': {},
                }

            # PUSH IN COL_NAME => TYPE KEYS UNDER TABLE
            container[row['table_name']]['columns'][row['column_name']] = row['type']

            # APPEND PRIMARY KEYS WHEN APPRIPRIATE
            if row['kind'] != 'regular':
                container[row['table_name']]['indexing'][row['kind']] = row['column_name']

        # FINALLY, ADD TABLE ROW COUNT
        for table_name in container.keys():
            container[table_name]['n_rows'] = cassandra.count(f"SELECT COUNT(*) FROM {keyspace_name}.{table_name}")

        return container

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error
    
########################################################################################################
########################################################################################################
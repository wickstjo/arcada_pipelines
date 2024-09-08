from cassandra.cluster import Cluster
from utils.misc import load_global_config

# LOAD THE GLOBAL CONFIG & STITCH TOGETHER THE CASSANDRA CONNECTION STRING
global_config = load_global_config()
cassandra_brokers = [(host, int(port)) for host, port in (item.split(':') for item in global_config.cluster.cassandra_brokers)]

# HIDE MANAGEMENT KEYSPACES AND TABLES
HIDE_SYSTEM_TABLES = global_config.backend.hide_auxillary
SYSTEM_TABLES = ['system_auth', 'system_schema', 'system_distributed', 'system', 'system_traces']

########################################################################################################
########################################################################################################

class create_cassandra_instance:
    def __init__(self):
        cluster = Cluster(cassandra_brokers)
        self.instance = cluster.connect()

    ########################################################################################################
    ########################################################################################################

    # FULL DATABASE OVERVIEW (KEYSPACES)
    def db_overview(self):
        container = {}

        # PERFORM THE TABLE QUERY
        table_query = self.instance.execute(
            f"SELECT keyspace_name, table_name FROM system_schema.tables"
        )

        for row in table_query:

            # WHEN TOGGLED, FILTER OUT SYSTEM TABLES
            if HIDE_SYSTEM_TABLES and row.keyspace_name in SYSTEM_TABLES:
                continue

            if row.keyspace_name not in container:
                container[row.keyspace_name] = []

            container[row.keyspace_name].append(row.table_name)

        return container
    
    ########################################################################################################
    ########################################################################################################

    # KEYSPACE OVERVIEW (TABLES)
    def keyspace_overview(self, keyspace_name):
        container = {}

        # STOP & THROW ERROR IF KEYSPACE DOESNT EXIST
        if keyspace_name not in self.db_overview().keys():
            raise Exception(f"KEYSPACE '{keyspace_name}' DOES NOT EXIST")

        # PERFORM THE TABLE QUERY
        table_query = self.instance.execute(
            f"SELECT * FROM system_schema.columns WHERE keyspace_name= '{keyspace_name}'"
        )

        # LOOP IN TABLE STRUCTURES
        for row in table_query:

            # CREATE TABLE KEY IF IT DOESNT EXIST
            if row.table_name not in container:
                container[row.table_name] = {
                    'n_rows': None,
                    'columns': {},
                    'indexing': {},
                }

            # PUSH IN COL_NAME => TYPE KEYS UNDER TABLE
            container[row.table_name]['columns'][row.column_name] = row.type

            # APPEND PRIMARY KEYS WHEN APPRIPRIATE
            if row.kind != 'regular':
                # container[row.table_name]['indexing'].append(row.column_name)
                container[row.table_name]['indexing'][row.kind] = row.column_name

        # ADD TABLE ROW COUNT
        for table_name in container.keys():
            count_query = self.instance.execute(f"SELECT COUNT(*) FROM {keyspace_name}.{table_name}")
            container[table_name]['n_rows'] = count_query.one()[0]

        return container

    ########################################################################################################
    ########################################################################################################

    # TABLE OVERVIEW
    def table_overview(self, keyspace_name, table_name):
        container = []

        # FETCH KEYSPACE/TABLE INFO FOR VERIFICATION
        db_content = self.db_overview()

        # IF KEYSPACE DOES NOT EXIST, THROW ERROR
        if keyspace_name not in db_content.keys():
            raise Exception(f"KEYSPACE '{keyspace_name}' DOES NOT EXIST")
        
        # IF TABLE DOES NOT EXIST, THROW ERROR
        if table_name not in db_content[keyspace_name]:
            raise Exception(f"TABLE '{keyspace_name}.{table_name}' DOES NOT EXIST")

        # ADD ROWS FROM HEAD
        # head_query = self.instance.execute(f"SELECT * FROM {keyspace_name}.{table_name} LIMIT {row_limit}")

        return container
    
    ########################################################################################################
    ########################################################################################################

    # CREATE A NEW KEYSPACE
    def create_keyspace(self, keyspace_name):
        self.instance.execute("""
            CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {
                'class': 'SimpleStrategy', 
                'replication_factor': '1'
            };
        """ % keyspace_name).all()

    ########################################################################################################
    ########################################################################################################

    # CREATE TABLE QUERY
    def create_table(self, keyspace_name, table_name, columns, indexing):

        # FETCH KEYSPACE/TABLE INFO FOR VERIFICATION
        db_content = self.db_overview()

        # IF KEYSPACE DOES NOT EXIST, CREATE IT
        if keyspace_name not in db_content.keys():
            self.create_keyspace(keyspace_name)
            db_content[keyspace_name] = {}

        # MAKE SURE PRIMARY KEYS ARE OK
        for key in indexing:
            col_list = list(columns.keys())
            
            if key not in col_list:
                raise Exception(f"PRIMARY KEY '{key}' IS NOT A VALID COLUMN")
        
        # MAKE SURE A PROPER CASSANDRA DOMAIN WAS PROVIDED
        if table_name in db_content[keyspace_name]:
            raise Exception('TABLE ALREADY EXISTS')

        # BASE QUERY
        query = f'CREATE TABLE {keyspace_name}.{table_name} ('
        
        # LOOP IN COLUMNS
        for column_name, column_type in columns.items():
            query += f'{column_name} {column_type}, '
            
        # ADD PRIMARY KEYS
        key_string = ', '.join(indexing)
        query += f'PRIMARY KEY({key_string}));'

        # CREATE THE TABLE
        self.instance.execute(query)

########################################################################################################
########################################################################################################


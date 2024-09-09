from cassandra.cluster import Cluster
import utils.misc as misc
import re

# LOAD THE GLOBAL CONFIG & STITCH TOGETHER THE CASSANDRA CONNECTION STRING
global_config = misc.load_global_config()
CASSANDRA_BROKERS = [(host, int(port)) for host, port in (item.split(':') for item in global_config.cluster.cassandra_brokers)]
VERBOSE = global_config.pipeline.verbose_logging

########################################################################################################
########################################################################################################

class create_cassandra_instance:
    def __init__(self):
        cluster = Cluster(CASSANDRA_BROKERS)
        self.instance = cluster.connect()

    ########################################################################################################
    ########################################################################################################

    # FREELY EXECUTE ANY CQL QUERY
    def query(self, query):
        return self.instance.execute(query)

    ########################################################################################################
    ########################################################################################################
    
    # CASSANDRA DRIVER ERRORS ARE VERY MESSY
    # THIS ATTEMPT TO PARSE THEM TO MAKE EVERYTHING MORE HUMAN-READABLE
    def parse_error(self, error):
        stringified_error = str(error)
        
        # TRY TO REGEX MATCH THE ERROR PATTERN
        match = re.search(r'message="(.+)"', stringified_error)

        # MATCH FOUND, RETURN ISOLATED ERROR MSG
        if match:
            return match.group(1)
        
        # OTHERWISE, RETURN THE WHOLE THING
        return stringified_error
    
    ########################################################################################################
    ########################################################################################################

    # READ DATA FROM THE DATABASE
    def read(self, query: str) -> list[dict]:
        try:
            container = []

            # PERFORM THE TABLE QUERY
            query_result = self.instance.execute(query)

            # PARSE EACH ROW AS A DICT
            for item in query_result:
                container.append(item._asdict())

            if VERBOSE: misc.log('[CASSANDRA] READ FROM DATABASE')

            return container
        
        # SAFELY CATCH ERRORS
        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA] READ ERROR => {parsed_error}')
    
    ########################################################################################################
    ########################################################################################################

    # FULL DATABASE OVERVIEW (KEYSPACES)
    def write(self, keyspace_table: str, row: dict):
        try:

            # SPLIT THE KEYS & VALUES
            columns = list(row.keys())
            values = list(row.values())

            # STITCH TOGETHER THE QUERY STRING
            query_string = f'INSERT INTO {keyspace_table} ('
            query_string += ', '.join(columns)
            query_string += ') values ('
            query_string += ', '.join(['?'] * len(columns))
            query_string += ');'
            
            # CONSTRUCT A PREPARED STATEMENT & EXECUTE THE DB WRITE
            prepared_statement = self.instance.prepare(query_string)
            self.instance.execute(prepared_statement, values)

            if VERBOSE: misc.log('[CASSANDRA] WROTE TO DATABASE')
        
        # SAFELY CATCH ERRORS
        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA] WRITE ERROR => {parsed_error}')
from common import misc, cassandra_utils
from common.testing import unittest_base

class validation_tests(unittest_base):
    def test_dataset_00_schema(self):

        # WHAT SCHEMA WE EXPECT THE INPUT TO FOLLOW
        reference_schema = {
            'db_table': str,
            'stock_symbol': str,
            'timestamps': {
                'start': str,
                'end': str,
            },
            'min_length_threshold': int,
        }
        
        # MAKE SURE INPUT DICT FITS REFERENCE SCHEMA
        self.validate_schema(self.input_params, reference_schema)

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_01_timestamp_format(self):
        length_error = lambda x: f"TIMESTAMP '{x}' DOES NOT FOLLOW THE FORMAT '%Y-%m-%d %H:%M:%S'"
        unix_error = lambda x: f"TIMESTAMP '{x}' COULD NOT BE CAST TO UNIX FORMAT"

        for key, value in self.input_params['timestamps'].items():

            # CHECK LENGTH FOR '%Y-%m-%d %H:%M:%S' FORMAT
            self.assertTrue(len(value) == 19, msg=length_error(key))

            # MAKE SURE WE CAN CONVERT IT TO AN UNIX TIMESTAMP
            try:
                misc.unix_ts(value)
            except Exception as e:
                self.fail(unix_error(key))

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_02_timestamp_order(self):

        # CONVERT DATESTRINGS TO UNIX TIMESTAMPS
        start_ts: int = misc.unix_ts(self.input_params['timestamps']['start'])
        end_ts: int = misc.unix_ts(self.input_params['timestamps']['end'])

        # MAKE SURE END IS LARGER THAN START
        self.assertTrue(start_ts < end_ts)

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_03_cassandra_connection(self):
        try:
            cassandra_utils.create_instance()
        except Exception as e:
            self.fail('COULD NOT CONNECT TO CASSANDRA CLUSTER')


    ### TODO MOCK CALL TO REAL FUNC WITH
    #               FAKE PARAMS
    #               REAL PARAMS



    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_04_dataset_min_length(self):
        db_table = self.input_params['db_table']
        stock_symbol = self.input_params['stock_symbol']
        start_date = self.input_params['timestamps']['start']
        end_date = self.input_params['timestamps']['end']
        min_row_count = self.input_params['min_length_threshold']

        # MAKE SURE MINIMUM THRESHOLD IS MET
        minimum_threshold: int = 5
        threshold_error = f"ARG 'min_length_threshold' MUST BE LARGER THAN {minimum_threshold}, GOT {min_row_count}"
        self.assertTrue(min_row_count > minimum_threshold, msg=threshold_error)
        
        # STITCH TOGETHER CQL QUERY STRING
        # NOTICE THAT THIS IS A COUNT QUERY, NOT FETCHING THE DATA ITSELF
        query_string: str = f"""
            SELECT count(*) FROM {db_table}
            WHERE symbol = '{stock_symbol}'
            AND timestamp >= '{start_date}'
            AND timestamp <= '{end_date}' 
            ORDER BY timestamp ASC
            ALLOW FILTERING
        """

        # FETCH THE DATASET AND VERIFY THAT ITS IN CHRONOLOGICAL ORDER
        cassandra = cassandra_utils.create_instance()
        dataset_length: int = cassandra.count(query_string)

        # MAKE SURE MINIMUM LENGTH WAS REACHED
        dataset_error = f"QUERY DID NOT YIELD A DATASET OF SUFFICIENT LENGTH (MIN EXPECTED {min_row_count}, GOT {dataset_length})"
        self.assertTrue(dataset_length >= min_row_count, msg=dataset_error)

    ##############################################################################################################
    ##############################################################################################################

    def test_dataset_05_ascending_order(self):
        db_table = self.input_params['db_table']
        stock_symbol = self.input_params['stock_symbol']
        start_date = self.input_params['timestamps']['start']
        end_date = self.input_params['timestamps']['end']
        min_row_count = self.input_params['min_length_threshold']
        
        # STITCH TOGETHER CQL QUERY STRING
        # NOTICE THAT THIS IS A COUNT QUERY, NOT FETCHING THE DATA ITSELF
        query_string: str = f"""
            SELECT * FROM {db_table}
            WHERE symbol = '{stock_symbol}'
            AND timestamp >= '{start_date}'
            AND timestamp <= '{end_date}' 
            ORDER BY timestamp ASC
            LIMIT {min_row_count}
            ALLOW FILTERING
        """

        # FETCH A SMALL SUBSET FROM THE DATASET
        cassandra = cassandra_utils.create_instance()
        subset: int = cassandra.read(query_string)

        # LOOP THROUGH SEQUENTIAL ENTRYPAIRS
        for nth in range(1, len(subset)):
            predecessor: dict = subset[nth-1]['timestamp']
            successor: dict = subset[nth]['timestamp']

            # MAKE SURE TIMESTAMPS ARE IN ASCENDING ORDER
            order_error = f"DATASET NOT IN ASCENDING ORDER ({predecessor} !< {successor})"
            self.assertTrue(predecessor < successor, msg=order_error)

    ##############################################################################################################
    ##############################################################################################################
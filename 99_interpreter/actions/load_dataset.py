from common import misc, cassandra_utils
from common.testing import unittest_base

def load_dataset(db_table: str, stock_symbol: str, timestamps: dict, min_row_count: int):
    start_date: str = timestamps['start']
    end_date: str = timestamps['end']
    
    # MAKE SURE TIMESTAMPS MAKE SENSE
    start_ts: int = misc.unix_ts(start_date)
    end_ts: int = misc.unix_ts(end_date)
    assert start_ts < end_ts, f"ARG 'end_date' IS NOT LARGER THAN 'start_date' ({end_date} > {start_date})"
    
    # STITCH TOGETHER CQL QUERY STRING
    query_string: str = f"""
        SELECT * FROM {db_table}
        WHERE symbol = '{stock_symbol}'
        AND timestamp >= '{start_date}'
        AND timestamp <= '{end_date}' 
        ORDER BY timestamp ASC
        ALLOW FILTERING
    """

    # FETCH THE DATASET AND VERIFY THAT ITS IN CHRONOLOGICAL ORDER
    cassandra = cassandra_utils.create_instance()
    dataset: list[dict] = cassandra.read(query_string, sort_by='timestamp')

    # MAKE SURE MINIMUM ROW COUNT IS MET
    row_count: int = len(dataset)
    assert row_count >= min_row_count, f'MINIMUM ROW COUNT NOT MET ({row_count} < {min_row_count})'

    return dataset


#####################################################################################
#####################################################################################


class validation_tests(unittest_base):
    def test_first(self):
        print(self.input_args)
        self.assertEqual(True, True)
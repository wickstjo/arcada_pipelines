from dataclasses import dataclass
from funcs.cassandra_utils import create_cassandra_instance

########################################################################################
########################################################################################

@dataclass(frozen=True)
class state:

    n_threads: int = 8
    report_breakpoint: int = 100

    source_dataset: str = 'finance_historical.csv'
    cassandra_table: str = 'john.historical_training_data'

########################################################################################
########################################################################################

cassandra = create_cassandra_instance()
result = cassandra.read(f'SELECT * FROM {state.cassandra_table}', sort_by='timestamp')

for item in result:
    print(item['timestamp'])
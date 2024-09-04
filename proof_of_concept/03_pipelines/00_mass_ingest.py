import utils.dataset_utils as dataset_utils
from utils.cassandra_utils import create_cassandra_instance
from utils.misc import log
from utils.types import TO_NAMESPACE

########################################################################################
########################################################################################

local_config = TO_NAMESPACE({

    # HOW MANY THREADS SHOULD WE USE?
    'n_threads': 4,

    # HOW LONG TO WAIT BETWEEN EVENTS
    'dataset': 'foo.csv',

    # WHAT TABLE DO YOU WANT TO WRITE DATA TO?
    'db_table': 'testing_namespace.testing_table'
})

########################################################################################
########################################################################################

try:
    pass

    # USE MULTIPLE THREADS
    # CREATE MULTIPLE CASSANDRA CLIENTS
    # LOAD DATASET
    # INGEST
    # GIVE OCCASIONAL REPORTS OF STATUS

# TERMINATE MAIN PROCESS AND KILL HELPER THREADS
except KeyboardInterrupt:
    log('DATA INGESTION MANUALLY KILLED..', True)
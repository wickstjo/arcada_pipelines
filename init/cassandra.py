import requests, json, time
from cassandra.cluster import Cluster, ConsistencyLevel, ExecutionProfile, EXEC_PROFILE_DEFAULT, dict_factory #, BatchStatement
import h5py, numpy as np

###########################################################################################################
###########################################################################################################

cassandra_machines = [204, 218, 163] # 218, 163, 149
n_replication = 1

###########################################################################################################
###########################################################################################################

cluster = Cluster(
    contact_points=[ ('192.168.1.' + str(x), 9042) for x in cassandra_machines ],
    idle_heartbeat_interval=0,
    execution_profiles={
        EXEC_PROFILE_DEFAULT: ExecutionProfile(
            consistency_level=ConsistencyLevel.ALL,
            row_factory=dict_factory
        )
    }
)

instance = cluster.connect()

instance.execute("""
CREATE KEYSPACE IF NOT EXISTS surface_data WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': '%s'
};
""" % n_replication).all()

#################################
#################################

instance.execute("""
CREATE TABLE IF NOT EXISTS surface_data.sensor_1A (
    timestamp text,
    serial_number text,
    vector list<double>,
    PRIMARY KEY(timestamp, serial_number)
);
""").all()

#################################
#################################

instance.execute("""
CREATE TABLE IF NOT EXISTS surface_data.defects (
    timestamp text,
    tensor_hash text,
    cable_sector text,
    tile_max double,
    tile_min double,
    tile_delta double,
    tile_mean double,
    n_defects int,
    PRIMARY KEY(timestamp, cable_sector, tensor_hash)
);
""").all()

instance.execute('SELECT * FROM system_schema.keyspaces;').all()

cluster.refresh_schema_metadata()
print(cluster.metadata.all_hosts())
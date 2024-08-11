import requests, json, time
from confluent_kafka.admin import AdminClient, NewPartitions, NewTopic
from confluent_kafka import TopicPartition
from cassandra.cluster import Cluster, ConsistencyLevel, ExecutionProfile, EXEC_PROFILE_DEFAULT, dict_factory #, BatchStatement

import multiprocessing
from confluent_kafka.schema_registry import SchemaRegistryClient, avro
from confluent_kafka import SerializingProducer
import h5py, numpy as np
import threading

###########################################################################################################
###########################################################################################################





kafka_machines = [24] # 204, 218, 163, 149
kafka_registry_URI = 'http://192.168.1.24:8181'

kafka_partitions = 4
kafka_replication = 1



cassandra_machines = [204, 218, 163, 149] # 204, 218, 163, 149

n_replication = 1





###########################################################################################################
###########################################################################################################

kafka_brokers_URI = ','.join(['192.168.1.' + str(x) + ':9092' for x in kafka_machines])
kafka_topic = 'surface_data.sensor_1A'

admin_client = AdminClient({
    'bootstrap.servers': kafka_brokers_URI
})

def create_schema(name, schema):
    result = requests.post(kafka_registry_URI + '/subjects/' + name + '/versions', json={
        'schema': json.dumps(schema),
        "schemaType": "AVRO",
    })
    
    print('STATUS:\t\t', result.status_code)
    print('RESPONSE:\t', result.json())

def query_topics():
    container = {}
    
    for name, parts in admin_client.list_topics().topics.items():
        container[name] = len(parts.partitions)
    
    # print(json.dumps(container, indent=4))
    
    return container

def create_topic(name, partitions, replication):
    
    # CHECK CURRENT TOPICS
    topic_data = query_topics()
    
    # STOP IF TOPIC ALREADY EXISTS
    if name in topic_data:
        # raise Exception('ERROR: THIS TOPIC ALREADY EXISTS')
        print('ERROR: THIS TOPIC ALREADY EXISTS')

    # OTHERWISE, CREATE IT
    admin_client.create_topics(
        new_topics=[NewTopic(
            topic=name,
            num_partitions=kafka_partitions,
            replication_factor=replication
        )]
    )
    
    return True

def set_partitions(topic_name, new_partition_count):
    
    # CHECK CURRENT TOPICS
    topic_data = query_topics()
    
    # MAKE SURE TOPIC EXISTS
    if topic_name not in topic_data:
        # raise Exception('ERROR: TOPIC DOES NOT EXIST')
        print('ERROR: TOPIC DOES NOT EXIST')
    
    # MAKE SURE NEW PARTITION NUM IS GREATER THAN BEFORE
    if new_partition_count <= topic_data[topic_name]:
        # raise Exception(f'ERROR:  NEW PARTITION NUM MUST BE GREATER THAN OLD ({topic_data[topic_name]})')
        print(f'ERROR:  NEW PARTITION NUM MUST BE GREATER THAN OLD ({topic_data[topic_name]})')
    
    # OTHERWISE, SET NEW PARTITION COUNT
    admin_client.create_partitions(
        new_partitions=[NewPartitions(
            topic=topic_name,
            new_total_count=new_partition_count,
        )]
    )
    
    return True

create_schema(
    name=kafka_topic, 
    schema={
        "namespace": "schemas.surface_data",
        "type": "record",
        "name": "sensor_1A",
        "fields": [
            {
                "name": "timestamp",
                "type": "string"
            },
            {
                "name": "serial_number",
                "type": "string"
            },
            {
                "name": "datapoints",
                "type": {
                    "type": "array",
                    "items": "double"
                }
            }
        ]
    }
)

create_schema(
    name='surface_data.defective_tile', 
    schema={
        "namespace": "schemas.surface_data",
        "type": "record",
        "name": "defective_tile",
        "fields": [
            {
                "name": "timestamp",
                "type": "string"
            },
            {
                "name": "tensor_hash",
                "type": "string"
            },
            {
                "name": "tensor",
                "type": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": "double"
                        }
                    }
                }
            }
        ]
    }
)

create_topic(
    name=kafka_topic,
    partitions=kafka_partitions,
    replication=kafka_replication
)

create_topic(
    name='surface_data.defects',
    partitions=kafka_partitions,
    replication=kafka_replication
)

set_partitions(topic_name='surface_data.sensor_1A', new_partition_count=kafka_partitions)

time.sleep(3)

# CREATE KAFKA REGISTRY CLIENT
schema_registry = SchemaRegistryClient({
    'url': kafka_registry_URI
})

# FETCH SCHEMA STRING FROM REGISTRY
schema_string = schema_registry.get_latest_version(kafka_topic).schema.schema_str

# CREATE SERIALIZER
serializer = avro.AvroSerializer(schema_registry, schema_string)

# CREATE CLIENT
kafka_client = SerializingProducer({
    'bootstrap.servers': kafka_brokers_URI,
    'value.serializer': serializer,
})

# PUSH ROWS
for _ in range(200):
    kafka_client.produce(
        kafka_topic, 
        value={
            'timestamp': 'foo',
            'serial_number': 'bar',
            'datapoints': [1.0, 2.0, 3.0]
        },
    )

    # WAIT FOR ACK
    kafka_client.poll(1)
    print('PUSHED MESSAGE')

kafka_client.flush()

result = query_topics()
print(json.dumps(result, indent=4))

################
################

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
    thread_id text,
    nth_msg text,
    vector list<double>,
    PRIMARY KEY((thread_id, nth_msg))
);
""").all()

#################################
#################################

# instance.execute("""
# CREATE TABLE IF NOT EXISTS surface_data.defects (
#     timestamp text,
#     tensor_hash text,
#     cable_sector text,
#     tile_max double,
#     tile_min double,
#     tile_delta double,
#     tile_mean double,
#     n_defects int,
#     PRIMARY KEY(timestamp, cable_sector, tensor_hash)
# );
# """).all()

instance.execute('SELECT * FROM system_schema.keyspaces;').all()

cluster.refresh_schema_metadata()

print('\n##############################################\n')

for host in cluster.metadata.all_hosts():
    print(host)

print('\n##############################################\n')

# for nth_thread in range(1, 16+1):
#     print(nth_thread, instance.execute("SELECT COUNT(*) FROM surface_data.sensor_1A WHERE thread_id = '%s'" % nth_thread).all())

print('TOTAL', instance.execute('SELECT COUNT(*) FROM surface_data.sensor_1A').all())
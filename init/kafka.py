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

kafka_machines = [204, 218, 163, 149] # 218, 163, 149
kafka_partitions = 4
kafka_replication = 1

###########################################################################################################
###########################################################################################################

kafka_registry_URI = 'http://192.168.1.24:8181'
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
for _ in range(5):
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
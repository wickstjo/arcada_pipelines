from confluent_kafka import Consumer, Producer
import utils.misc as misc
from utils.thread_utils import create_process_beacon
from utils.cassandra_utils import create_cassandra_instance
from typing import Callable
import json

# LOAD THE GLOBAL CONFIG & STITCH TOGETHER THE KAFKA CONNECTION STRING
global_config = misc.load_global_config()
KAFKA_BROKERS = ','.join(global_config.cluster.kafka_brokers)
VERBOSE = global_config.pipeline.verbose_logging

###################################################################################################
###################################################################################################

class create_producer:

    # ON LOAD, CREATE KAFKA PRODUCER
    def __init__(self):
        self.kafka_client = Producer({
            'bootstrap.servers': KAFKA_BROKERS,
        })

        self.check_connection()

    # MAKE SURE KAFKA CONNECTION IS OK
    def check_connection(self):
        try:
            metadata = self.kafka_client.list_topics(timeout=2)
            return True
        except:
            raise Exception(f'COULD NOT CONNECT WITH KAFKA SERVER ({KAFKA_BROKERS})')

    # ON CONSUMER CALLBACK, DO..
    def ack_callback(self, error, message):
        if error:
            print('ACK ERROR', error)
        else:
            if VERBOSE: misc.log(f'[KAFKA] PUSHED EVENT')

    # DATA SERIALIZER: JSON/DICT => BYTES
    def json_serializer(self, json_data: dict) -> list[bool, bytes|str]:
        try:
            json_bytes = json.dumps(json_data).encode('UTF-8')
            return json_bytes
        except:
            raise Exception('[KAFKA] SERIALIZATION ERROR')

    # PUSH MESSAGE TO A KAFK TOPIC
    def push_msg(self, topic_name: str, data_dict: dict):

        # TRY TO CONVERT THE DICT TO BYTES
        bytes_data = self.json_serializer(data_dict)

        # THEN PUSH THE MESSAGE TO A KAFKA TOPIC
        self.kafka_client.produce(
            topic_name, 
            value=bytes_data,
            on_delivery=self.ack_callback,
        )

        # ASYNC ACKNOWLEDGE
        if global_config.pipeline.kafka.async_producer_ack:
            self.kafka_client.poll(1)
        
        # SYNCHRONOUS ACKNOWLEDGE
        else:
            self.kafka_client.flush()

###################################################################################################
###################################################################################################

class create_consumer:

    # ON LOAD, CREATE KAFKA CONSUMER CLIENT
    def __init__(self, kafka_topic: str|list[str]):

        # ARE WE SUBSCRIBING TO ONE TOPIC OR MORE? FORMAT ACCORDINGLY
        self.kafka_topic = [kafka_topic] if type(kafka_topic) == str else kafka_topic

        # MAKE SURE THE CONSUMER STRATEGY IS VALID
        if global_config.pipeline.kafka.consumer_stategy not in ['earliest', 'latest']:
            raise Exception(f'INCOHERENT CONSUMER STRATEGY ({global_config.pipeline.kafka.consumer_stategy})')

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            'bootstrap.servers': KAFKA_BROKERS,
            'group.id': ','.join(self.kafka_topic) + '.consumers',
            'enable.auto.commit': global_config.pipeline.kafka.consumer_auto_commit,
            'on_commit': self.ack_callback,
            'auto.offset.reset': global_config.pipeline.kafka.consumer_stategy,
            # 'auto.offset.reset': 'latest'
            # 'auto.offset.reset': 'earliest'
        })

        # MAKE SURE THE KAFKA CONNECTION IS OK
        self.check_connection()

        # FINALLY, SUBSCRIBE TO THE PROVIDED KAFKA TOPIC
        self.kafka_client.subscribe(self.kafka_topic, self.assigned, self.revoked, self.lost)

    # WHEN CLASS DIES, KILL THE KAFKA CLIENT
    def __del__(self):
        misc.log('[KAFKA] CONSUMER CLOSED')
        self.kafka_client.close()

    # PARTITION ASSIGNMENT SUCCESS
    def assigned(self, consumer, partition_data):
        if VERBOSE:
            partitions = [p.partition for p in partition_data]
            misc.log(f'[KAFKA] CONSUMER ASSIGNED PARTITIONS: {partitions}')

    # PARTITION ASSIGNMENT REVOKED
    def revoked(self, consumer, partition_data):
        if VERBOSE:
            partitions = [p.partition for p in partition_data]
            misc.log(f'[KAFKA] CONSUMER PARTITION ASSIGNMENT REVOKED: {partitions}')

    # PARTITION ASSIGNMENT LOST
    def lost(self, consumer, partition_data):
        misc.log(f'[KAFKA] CONSUMER ASSIGNMENT LOST: {consumer} {partition_data}')

    # MAKE SURE KAFKA CONNECTION IS OK
    def check_connection(self):
        try:
            metadata = self.kafka_client.list_topics(timeout=2)
            return True
        except:
            raise Exception(f'COULD NOT CONNECT WITH KAFKA SERVER ({KAFKA_BROKERS})') 

    # AUTO CALLBACK WHEN CONSUMER COMMITS MESSAGE
    def ack_callback(self, error, partitions):
        if error:
            print('ACK ERROR', error)
            return

    # DATA DESERIALIZER: BYTES => JSON DICT
    def json_deserializer(self, raw_bytes: bytes) -> list[bool, dict|str]:
        try:
            json_dict = json.loads(raw_bytes.decode('UTF-8'))
            return json_dict
        except:
            raise Exception('[KAFKA] DESERIALIZATION ERROR')

########################################################################################
########################################################################################

class create_flex_worker:

    # ON LOAD, CREATE KAFKA CONSUMER CLIENT
    def __init__(self, input_topic: str|list[str], include_kafka_producer: bool, include_cassandra: bool, include_yaml_config: bool):

        # SAVE TOPICS IN STATE
        self.input_topic = input_topic

        # ALWAYS CREATE A KAFKA CONSUMER
        self.consumer = create_consumer(input_topic)

        # WHAT SUPPORT STRUCTS SHOULD BE PROVIDED IN THE EVENT CALLBACK FUNC?
        # ORDER: KAFKA_PRODUCER, CASSANDRA_CLIENT, GLOBAL_CONFIG
        self.callback_support_structs = []

        # IF REQUESTED, CREATE A KAFKA PRODUCER
        if include_kafka_producer:
            self.producer = create_producer()
            self.callback_support_structs.append(self.producer)

        # IF REQUESTED, CREATE A CASSANDRA CLIENT
        if include_cassandra:
            self.cassandra = create_cassandra_instance()
            self.callback_support_structs.append(self.cassandra)

        # IF REQUESTED, PROVIDE THE GLOBAL CONFIG
        if include_yaml_config:
            self.callback_support_structs.append(global_config)

    def poll_next(self, beacon, handle_event):
        if VERBOSE: misc.log(f'[KAFKA] STARTED POLLING EVENTS (topic: {self.input_topic})')

        # KEEP POLLING WHILE THE THREAD LOCK IS ACTIVE
        while beacon.is_active():
            try:

                # POLL NEXT MESSAGE
                msg = self.consumer.kafka_client.poll(1)

                # NULL MESSAGE -- SKIP
                if msg is None:
                    continue

                # CATCH ERRORS
                if msg.error():
                    misc.log('[KAFKA] FAULTY EVENT RECEIVED', msg.error())
                    continue

                # IF AUTO-COMMITTING IS DISABLED
                # COMMIT THE EVENT TO PREVENT OTHERS FROM TAKING IT
                if not global_config.pipeline.kafka.consumer_auto_commit:
                    self.consumer.kafka_client.commit(msg, asynchronous=global_config.pipeline.kafka.async_consumer_commit)

                # DESERIALIZE THE MESSAGE, AND CHECK WHICH TOPIC IT CAME FROM
                deserialized_dict: dict = self.consumer.json_deserializer(msg.value())
                topic_name: str = msg.topic()

                # HANDLE THE EVENT VIA CALLBACK FUNC
                if VERBOSE: misc.log(f'[KAFKA] EVENT RECEIVED ({topic_name})')

                # RUN THE CALLBACK FUNC
                try:
                    handle_event(topic_name, deserialized_dict, self.callback_support_structs)

                # THROW SPECIFIC ERROR WHEN USER TRIES TO DESTRUCTURE TOO MANY/FEW ARGS FROM THE SUPPORT_STRUCTS LIST
                except ValueError as error:
                    misc.log(f'[CALLBACK] SUPPORT_STRUCTS EXTRACTION ERROR: {error}')
                except Exception as error:
                    misc.log(f'[CALLBACK] ERROR: {error}')

                if VERBOSE: misc.log(f'[KAFKA] EVENT HANDLED')

            # SILENTLY DEAL WITH OTHER ERRORS
            except Exception as error:
                print('[KAFKA] PRODUCER_CONSUMER ERROR:', error)
                continue
            
        # LOCK WAS KILLED, THEREFORE THREAD LOOP ENDS
        misc.log('[KAFKA] POLLING HAS CORRECTLY ENDED..')

########################################################################################
########################################################################################

def start_flex_consumer(input_topic: str, handle_event: Callable, include_kafka_producer: bool = False, include_cassandra: bool = False, include_yaml_config: bool = False):

    # CREATE THE KAKFA CLIENT & CONTROL LOCK
    kafka_client = create_flex_worker(input_topic, include_kafka_producer, include_cassandra, include_yaml_config)
    beacon = create_process_beacon()

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_client.poll_next(beacon, handle_event)

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        beacon.kill()
        misc.log('[KAFKA] POLLING HAS CORRECTLY ENDED..', True)


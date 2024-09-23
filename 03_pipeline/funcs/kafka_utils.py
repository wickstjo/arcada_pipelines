from confluent_kafka import Consumer, Producer
import funcs.misc as misc
import funcs.thread_utils as thread_utils
import json

# LOAD THE GLOBAL CONFIG & STITCH TOGETHER THE KAFKA CONNECTION STRING
global_config = misc.load_global_config()
KAFKA_BROKERS = ','.join(global_config.cluster.kafka_brokers)
VERBOSE = global_config.pipeline.verbose_logging

###################################################################################################
###################################################################################################

class create_kafka_producer:

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
            target_topic: str = message.topic()
            if VERBOSE: misc.log(f'[KAFKA] PUSHED EVENT ({target_topic})')

    # DATA SERIALIZER: JSON/DICT => BYTES
    def json_serializer(self, json_data: dict) -> list[bool, bytes|str]:
        try:
            return json.dumps(json_data).encode('UTF-8')
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

class create_kafka_consumer:

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
            return json.loads(raw_bytes.decode('UTF-8'))
        except:
            raise Exception('[KAFKA] DESERIALIZATION ERROR')

    # START VACUUMING DATA FROM KAFKA
    def poll_next(self, beacon, handle_event):
        if VERBOSE: misc.log(f'[KAFKA] STARTED POLLING ({self.kafka_topic})')

        # KEEP POLLING WHILE THE THREAD LOCK IS ACTIVE
        while beacon.is_active():
            try:

                # POLL NEXT MESSAGE
                msg = self.kafka_client.poll(1)

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
                    self.kafka_client.commit(msg, asynchronous=global_config.pipeline.kafka.async_consumer_commit)

                # DESERIALIZE THE MESSAGE, AND CHECK WHICH TOPIC IT CAME FROM
                deserialized_dict: dict = self.json_deserializer(msg.value())
                topic_name: str = msg.topic()

                if VERBOSE:
                    misc.log(f'[KAFKA] EVENT RECEIVED ({topic_name})')

                # RUN THE CALLBACK FUNC
                try:
                    handle_event(topic_name, deserialized_dict)

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

def start_kafka_consumer(create_pipeline_state):

    # CREATE A PROCESS BEACON TO KILL OFF HELPER THREADS
    beacon = thread_utils.create_process_beacon()

    # INSTANTIATE THE PIPELINE STATE
    state = create_pipeline_state(beacon)

    # MAKE SURE INPUT_TOPICS IS DEFINED
    # MAKE SURE THE HANDLE_EVENTS METHOD IS DEFINED
    assert hasattr(state, 'kafka_input_topics'), "STATE ERROR: YOU MUST DEFINE THE STATE VARIABLE 'kafka_input_topics'"
    assert hasattr(state, 'on_kafka_event'), "STATE ERROR: YOU MUST DEFINE THE STATE METHOD 'on_kafka_event'"

    # CREATE THE KAKFA CONSUMER & CONTROL LOCK
    kafka_client = create_kafka_consumer(state.kafka_input_topics)

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_client.poll_next(beacon, state.on_kafka_event)

    except AssertionError as error:
        misc.log(f'[ASSERT FAIL] {error}')

    except Exception as error:
        misc.log(f'[CRASH]: {error}')
    
    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        beacon.kill()
        misc.log('[MAIN] PROCESS WAS MANUALLY ENDED..', True)
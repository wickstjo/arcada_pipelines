from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, TopicPartition
import funcs.constants as constants
import funcs.misc as misc

# LOAD THE GLOBAL CONFIG & STITCH TOGETHER THE KAFKA CONNECTION STRING
global_config: dict = constants.global_config()
kafka_brokers = ','.join(global_config.cluster.kafka_brokers)

########################################################################################################
########################################################################################################

class create_admin_client:
    def __init__(self):

        # ATTEMPT TO CONNECT TO THE CLUSTER
        self.instance = AdminClient({
            'bootstrap.servers': kafka_brokers,
        })

        self.check_connection()

    ########################################################################################################
    ########################################################################################################

    # MAKE SURE KAFKA CONNECTION IS OK
    def check_connection(self):
        try:
            metadata = self.instance.list_topics(timeout=2)
            return True
        except Exception as error:
            raise Exception(f'[KAFKA CONNECTION ERROR] {error}') 

    ########################################################################################################
    ########################################################################################################

    def summarize_topics(self):
        try:
            formatted_topics = {}
            
            # CREATE A TEMP CONSUMBER TO READ TOPIC OFFSETS
            temp_consumer = Consumer({
                'bootstrap.servers': kafka_brokers,
                'group.id': 'offset_checker_group',
                'auto.offset.reset': 'earliest'
            })

            # PARSE THROUGH TOPIC DETAILS
            for topic_name, topic_metadata in self.instance.list_topics().topics.items():

                # SKIP THE OFFSETS TOPIC
                if global_config.backend.hide_auxillary and topic_name == '__consumer_offsets':
                    continue

                # NAME & THE NUMBER OF PARTITIONS
                formatted_topics[topic_name] = {
                    'num_partitions': len(topic_metadata.partitions),
                    'offsets': {}
                }

                # PARTITION OFFSETS
                for partition_id, _ in topic_metadata.partitions.items():
                    tp = TopicPartition(topic_name, partition_id)
                    earliest, latest = temp_consumer.get_watermark_offsets(tp, timeout=10)
                    # container[topic_name]['offsets'][partition_id] = tp.offset

                    formatted_topics[topic_name]['offsets'][partition_id] = {
                        'earliest': earliest,
                        'latest': latest
                    }
            
            return formatted_topics
        
        except Exception as error:
            raise Exception(f'[TOPIC SUMMARY ERROR] {error}') 
    
    ########################################################################################################
    ########################################################################################################

    def topic_exists(self, target_topic):
        try:

            # FISH OUT ALL EXISTING TOPIC NAMES
            existing_topics = [name for name, _ in self.instance.list_topics().topics.items()]

            # RETURN TRUE FOR DUPLICATES, OTHERWISE FALSE
            for topic in existing_topics:
                if topic == target_topic:
                    return True
            
            return False
        
        except Exception as error:
            raise Exception(f'[TOPIC EXISTS ERROR] {error}') 
    
    ########################################################################################################
    ########################################################################################################
    
    # ATTEMPT TO CREATE A NEW TOPIC
    def create_topic(self, name, num_partitions):
        try:

            # THROW ERROR IF TOPIC ALREADY EXISTS
            if self.topic_exists(name):
                raise Exception('TOPIC ALREADY EXISTS')

            # OTHERWISE, CREATE IT
            self.instance.create_topics(
                new_topics=[NewTopic(
                    topic=name,
                    num_partitions=num_partitions,
                    replication_factor=1,
                )]
            )

        except Exception as error:
            raise Exception(f'[CREATE TOPIC ERROR] {error}') 

    ########################################################################################################
    ########################################################################################################


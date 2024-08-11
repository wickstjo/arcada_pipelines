from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, TopicPartition

# KAFKA INSTANCES
kafka_ports = [11001, 11002]
kafka_brokers = ','.join([f'localhost:{str(x)}' for x in kafka_ports])

class create_admin_client:
    def __init__(self):

        # ATTEMPT TO CONNECT TO THE CLUSTER
        self.instance = AdminClient({
            'bootstrap.servers': kafka_brokers,
        })

    # FETCH ALL EXISTING TOPICS
    def topics_overview(self):
        container = {}
        
        # PARSE THROUGH TOPIC DETAILS
        for topic_name, topic_metadata in self.instance.list_topics().topics.items():

            # NAME & THE NUMBER OF PARTITIONS
            container[topic_name] = {
                'num_partitions': len(topic_metadata.partitions),
                'offsets': {}
            }

            # PARTITION OFFSETS
            for partition_id, _ in topic_metadata.partitions.items():
                tp = TopicPartition('eyylmao', partition_id)
                container[topic_name]['offsets'][partition_id] = tp.offset
        
        return container
    
    # CHECK IF TOPIC ALREADY EXISTS
    def topic_exists(self, target_topic):

        # FISH OUT ALL EXISTING TOPIC NAMES
        existing_topics = [name for name, _ in self.instance.list_topics().topics.items()]

        # RETURN TRUE FOR DUPLICATES, OTHERWISE FALSE
        for topic in existing_topics:
            if topic == target_topic:
                return True
        
        return False
    
    # ATTEMPT TO CREATE A NEW TOPIC
    def create_topic(self, name, num_partitions):

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
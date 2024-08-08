from confluent_kafka import DeserializingConsumer, SerializingProducer
from confluent_kafka.error import ConsumeError
import json

# KAFKA BROKER URL
KAFKA_URL = 'kafka1:9092'

class producer():
    def __init__(self):
        self.client = SerializingProducer({
            'bootstrap.servers': KAFKA_URL,
            'value.serializer': self.serializer,
        })

    # SERIALIZE INPUT -- JSON DATA
    def serializer(self, input_dict, context):
        return json.dumps(input_dict).encode('utf-8')

    # SUBMISSION ACK
    def delivery_callback(self, error, message):
        if error is not None:
            print(f'CALLBACK ERROR: {error}')
        else:
            print(f'Produced record to topic {message.topic()} partition [{message.partition()}] @ offset {message.offset()}')

    # PUSH DATA TO TOPIC
    def push(self, params):
        self.client.produce(
            params['topic'],
            value=params['message'],
            on_delivery=self.delivery_callback
        )

class consumer():
    def __init__(self, params):
        self.client = DeserializingConsumer({
            'bootstrap.servers': KAFKA_URL,
            'value.deserializer': self.deserializer,
            'group.id': params['group'],
            # 'enable.auto.commit': False,
            'auto.offset.reset': 'earliest'
        })

        # SUBSCRIBE TO TOPIC FEED
        self.client.subscribe([params['topic']])

    # INPUT SERIALIZER
    def deserializer(self, input_bytes, context):
        return json.loads(input_bytes.decode('utf-8'))
    
    # START CONSUMING TOPIC DATA
    def start(self, callback):
        while True:
            try:
                msg = self.client.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    print("ERROR: {}".format(msg.error()))
                    continue

                foo = msg.value()
                print('RECEIVED NEW JOB')
                callback(foo)

            # IGNORE TOPIC NOT CREATED ERROR
            except ConsumeError:
                print('WAITING FOR TOPIC TO BE CREATED..')
                pass

            # MANUALLY KILL THE WORKER
            except KeyboardInterrupt:
                break


        print('\nWORKER DIED..')
        self.client.close()
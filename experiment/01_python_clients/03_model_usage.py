import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC
from utilz.misc import log

import torch, io
from PIL import Image
from numpy import asarray

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # KAFKA TOPICS
    'input_topic': 'model_usage',
    'output_topic': 'model_evaluation',

    # WHICH YOLO MODEL TO USE?
    'yolo_model': 'custom-750k'
})

########################################################################################
########################################################################################

# LOAD THE INTENDED YOLO MODEL OUTSIDE THE FUNC -- FOR REPEATED USE
yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=f'./models/{config.yolo_model}.pt', trust_repo=True, force_reload=True)
hardware_device = yolo_model.parameters().__next__().device
log(f'LOADED MODEL ({config.yolo_model}) ON HARDWARE ({hardware_device})')

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):
    print(input_data)

    # EXTRACT THE IMAGE BYTES
    img_bytes = input_data['img_bytes']

    # CONVERT INPUT BYTES TO IMAGE & FEED IT TO THE MODEL
    img = Image.open(io.BytesIO(img_bytes))
    model_output = yolo_model.forward(asarray(img))

    # PUSH THE RESULTS TO THE EVALUATION TOPIC
    kafka_push(config.output_topic, {
        'timestamps': {
            'pre': model_output.t[0],
            'inf': model_output.t[1],
            'post': model_output.t[2],
        },
        'model': config.yolo_model,
        'dimensions': model_output.s
    })

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
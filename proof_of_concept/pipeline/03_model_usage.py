import utilz.kafka_clients as kafka_clients
from utilz.types import DICT_NAMESPACE, KAFKA_DICT, KAFKA_PUSH_FUNC
import utilz.yolo_utils as yolo_utils

########################################################################################
########################################################################################

config = DICT_NAMESPACE({

    # KAFKA TOPICS
    'input_topic': 'model_usage',
    'output_topic': 'post_processing',

    # WHICH YOLO MODEL TO USE?
    'yolo_model': 'yolo_custom_750k'
})

# LOAD THE YOLO MODEL FROM FILESYSTEM
yolo_model = yolo_utils.load_model(config.yolo_model)

########################################################################################
########################################################################################

# HANDLE INCOMING KAFKA EVENTS
def handle_event(input_data: KAFKA_DICT, kafka_push: KAFKA_PUSH_FUNC):

    # TERMINATE IF THE IMG_BYTES PROPERTY DOES NOT EXIST
    if 'img_bytes' not in input_data:
        raise Exception("INPUT MISSING 'img_bytes' PROPERTY")

    # OTHERWISE, CONVERT INPUT BYTES TO IMAGE & FEED IT TO THE MODEL
    model_input = yolo_utils.bytes_to_img(input_data['img_bytes'])
    model_output = yolo_model.forward(model_input)

    ####################################################################
    ####################################################################
    ####################################################################


    # TODO: FIGURE OUT HOW TO BEST DO THIS WITH DIFFERENT TYPES OF PREDICTIONS


    ####################################################################
    ####################################################################
    ####################################################################

    # PUSH THE RESULTS TO THE EVALUATION TOPIC
    kafka_push(config.output_topic, {
        'source': config.yolo_model,
        #'prediction': 'foo',
        'output': {
            'time_pre_processing': model_output.t[0],
            'time_inference': model_output.t[1],
            'time_post_processing': model_output.t[2],
            'dimensions': model_output.s
        },
    })

########################################################################################
########################################################################################

kafka_clients.start_consumer_producer(
    config.input_topic, handle_event
)
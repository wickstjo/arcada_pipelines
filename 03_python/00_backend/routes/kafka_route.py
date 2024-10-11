from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from common import constants
from ..funcs import kafka_admin_utils

########################################################################################################
########################################################################################################

router = APIRouter()
kafka_admin = kafka_admin_utils.create_instance()
global_config = constants.global_config()

########################################################################################################
########################################################################################################

@router.get('/kafka/')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return kafka_admin.summarize_topics()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error

########################################################################################################
########################################################################################################

@router.get('/kafka/consumers')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return kafka_admin.summarize_consumer_groups()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error

########################################################################################################
########################################################################################################

class Topic(BaseModel):
    name: str
    num_partitions: int

@router.post('/kafka/create')
async def foo(topic: Topic, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        kafka_admin.create_topic(topic.name, topic.num_partitions)

        return {
            'topic_name': topic.name,
            'num_partitions': topic.num_partitions
        }
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error
    
########################################################################################################
########################################################################################################

@router.get('/kafka/{topic_name}')
async def foo(topic_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK

        # FETCH ALL TOPICS
        all_topics = kafka_admin.summarize_topics()

        # RETURN ERROR IF TOPIC DOES NOT EXIST
        if topic_name not in all_topics:
            response.status_code = status.HTTP_404_NOT_FOUND
            return str('TOPIC DOES NOT EXIST')
        
        # OTHERWISE, RETURN TOPIC DETAILS
        return all_topics[topic_name]

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return error
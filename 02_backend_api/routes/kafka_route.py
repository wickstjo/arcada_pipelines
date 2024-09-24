from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import funcs.kafka_utils as kafka_utils
import funcs.constants as constants

########################################################################################################
########################################################################################################

router = APIRouter()
kafka_admin = kafka_utils.create_admin_client()
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

@router.get('/kafka/init')
async def foo(response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        container = []

        # LOOP THROUGH TOPICS LISTED IN THE GLOBAL CONFIG
        for topic in global_config.backend.create_on_init.kafka_topics:
            try:
                kafka_admin.create_topic(topic, 1)
                container.append(f"TOPIC '{topic}' CREATED")
            except:
                container.append(f"TOPIC '{topic}' ALREADY EXIST")
                
        return container
    
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
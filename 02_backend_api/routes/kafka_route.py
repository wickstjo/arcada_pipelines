from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import funcs.kafka_utils as kafka_utils
import funcs.misc as misc

########################################################################################################
########################################################################################################

router = APIRouter()
kafka_admin = kafka_utils.create_admin_client()
global_config = misc.load_global_config()

########################################################################################################
########################################################################################################

@router.get('/kafka/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return kafka_admin.topics_overview()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'KAFKA ROOT ERROR: {str(error)}'

########################################################################################################
########################################################################################################

class Topic(BaseModel):
    name: str
    num_partitions: int

@router.post('/kafka/create')
async def create_topic(topic: Topic, response: Response):
    try:
        response.status_code = status.HTTP_201_CREATED
        kafka_admin.create_topic(topic.name, topic.num_partitions)

        return {
            'topic_name': topic.name,
            'num_partitions': topic.num_partitions
        }
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'KAFKA CREATE ERROR: {str(error)}'

########################################################################################################
########################################################################################################

@router.get('/kafka/init')
async def initialize_default_content(response: Response):

    # READ WHAT TOPICS TO CREATE FROM THE GLOBAL CONFIG
    topics = global_config.backend.create_on_init.kafka_topics

    try:
        response.status_code = status.HTTP_201_CREATED
        container = []

        for topic in topics:
            try:
                kafka_admin.create_topic(topic, 1)
                container.append(f"TOPIC '{topic}' CREATED")
            except:
                container.append(f"TOPIC '{topic}' ALREADY EXIST")
                
        return container
    
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'KAFKA INIT ERROR: {str(error)}'
    
########################################################################################################
########################################################################################################

@router.get('/kafka/{topic_name}')
async def topic_overview(topic_name: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK

        # FETCH ALL TOPICS
        all_topics = kafka_admin.topics_overview()

        # RETURN ERROR IF TOPIC DOES NOT EXIST
        if topic_name not in all_topics:
            response.status_code = status.HTTP_404_NOT_FOUND
            return str('TOPIC DOES NOT EXIST')
        
        # OTHERWISE, RETURN TOPIC DETAILS
        return all_topics[topic_name]


    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return f'KAFKA TOPIC ERROR: {str(error)}'
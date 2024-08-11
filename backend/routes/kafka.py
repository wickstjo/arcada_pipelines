from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import utils.kafka as kafka_utils

########################################################################################################
########################################################################################################

router = APIRouter()
kafka_admin = kafka_utils.create_admin_client()

########################################################################################################
########################################################################################################

@router.get('/kafka/')
async def overview(response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return kafka_admin.topics_overview()

    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return str(error)

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
        return f'ERROR: {str(error)}'

########################################################################################################
########################################################################################################
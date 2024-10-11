import common.constants as constants
import requests, json

##############################################################################################
##############################################################################################

# LOAD THE GLOBAL CONFIG FOR SETTINGS & INITIALIZE COMPONENTS
global_config: dict = constants.global_config()
BACKEND_API = f'{global_config.endpoints.host}:{global_config.endpoints.ports.backend_api}'

def get_request(endpoint):
    try:
        result = requests.get(endpoint)
        
        print(json.dumps({
            'status': result.status_code,
            'data': result.json()
        }, indent=4) + '\n')

    except Exception as error:
        print(f'ERROR: {error}\n')

def post_request(endpoint, body):
    try:
        result = requests.post(endpoint, json=body)

        print(json.dumps({
            'status': result.status_code,
            'data': result.json()
        }, indent=4) + '\n')

    except Exception as error:
        print(f'ERROR: {error}\n')

##############################################################################################
##############################################################################################

cassandra_tables = [
    {
        "keyspace_name": "john",
        "table_name": "refined_stock_data",
        "columns": {
            "timestamp": "text",
            "symbol": "text",
            "high": "float",
            "low": "float",
            "open": "float",
            "close": "float",
            "adjusted_close": "float",
            "volume": "int",
        },
        "indexing": ["symbol", "timestamp"]
    }
]

for query in cassandra_tables:
    print(f"### CREATING CASSANDRA TABLE ({query['keyspace_name']}.{query['table_name']})")
    post_request(f'http://{BACKEND_API}/cassandra/create', query)

##############################################################################################
##############################################################################################

kafka_topics = [
    {
        "name": "data_refinery",
        "num_partitions": 1
    },
    {
        "name": "model_dispatch",
        "num_partitions": 1
    },
    {
        "name": "decision_synthesis",
        "num_partitions": 1
    },
    {
        "name": "drift_analysis",
        "num_partitions": 1
    }
]

for topic in kafka_topics:
    print(f"### CREATING KAFKA TOPIC ({topic['name']})")
    post_request(f'http://{BACKEND_API}/kafka/create', topic)

##############################################################################################
##############################################################################################

redis_keystore = [
    {
        'key': 'model_pipelines',
        'value': {

            # APPLE STOCK INPUT
            'aapl': {
                'pipe_4': [
                    {
                        'model_name': 'model_1',
                        'model_version': 'champion'
                    }
                ],
                'pipe_5': [
                    {
                        'model_name': 'model_2',
                        'model_version': 'champion'
                    },
                    {
                        'model_name': 'model_3',
                        'model_version': 'champion'
                    }
                ]
            }
        }
    },
    {
        'key': 'model_versions',
        'value': {
            'model_1': {
                'champion': 12,
            },
            'model_2': {
                'champion': 1,
            },
            'model_3': {
                'champion': 3,
            },
            'model_4': {
                'champion': 1,
            },
            'model_5': {
                'champion': 1,
            },
        }
    }
]

for kv_item in redis_keystore:
    print(f"### CREATING REDIS KEY ({kv_item['key']})")
    post_request(f'http://{BACKEND_API}/redis/create', kv_item)

##############################################################################################
##############################################################################################


# {

#     # AMAZON STOCK INPUT
#     'amzn': {
#         'pipe_1': [
#             {
#                 'model_name': 'model_1',
#                 'version_alias': 'champion'
#             }
#         ]
#     },

#     # META STOCK INPUT
#     'meta': {
#         'pipe_2': [
#             {
#                 'model_name': 'model_2',
#                 'version_alias': 'champion'
#             },
#             {
#                 'model_name': 'model_3',
#                 'version_alias': 'champion'
#             },
#             {
#                 'model_name': 'model_4',
#                 'version_alias': 'champion'
#             }
#         ],
#         'pipe_1': [
#             {
#                 'model_name': 'model_5',
#                 'version_alias': 'champion'
#             }
#         ]
#     },

#     # APPLE STOCK INPUT
#     'aapl': {
#         'pipe_4': [
#             {
#                 'model_name': 'model_6',
#                 'version_alias': 'champion'
#             }
#         ],
#         'pipe_5': [
#             {
#                 'model_name': 'model_7',
#                 'version_alias': 'champion'
#             },
#             {
#                 'model_name': 'model_8',
#                 'version_alias': 'champion'
#             }
#         ]
#     }
# }
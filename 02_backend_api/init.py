import requests, json

##############################################################################################
##############################################################################################

def get_request(endpoint):
    result = requests.get(endpoint)
    
    print(json.dumps({
        'status': result.status_code,
        'data': result.json()
    }, indent=4) + '\n')

def post_request(endpoint, body):
    result = requests.post(endpoint, json=body)

    print(json.dumps({
        'status': result.status_code,
        'data': result.json()
    }, indent=4) + '\n')

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
    post_request('http://193.166.180.240:3003/cassandra/create', query)

##############################################################################################
##############################################################################################

kafka_topics = [
    {
        "name": "model_dispatch",
        "num_partitions": 1
    }
]

for topic in kafka_topics:
    print(f"### CREATING KAFKA TOPIC ({topic['name']})")
    post_request('http://193.166.180.240:3003/kafka/create', topic)

##############################################################################################
##############################################################################################
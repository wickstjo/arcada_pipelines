import requests

######################################################################
######################################################################

result = requests.get('http://localhost:3003/kafka/init')

if result.status_code == 201:
    print('INITIALIZED KAFKA TOPICS')
    for item in result.json():
        print('\t', item)

######################################################################
######################################################################

result = requests.get('http://localhost:3003/cassandra/init')

if result.status_code == 201:
    print('INITIALIZED CASSANDRA TOPICS')
    for item in result.json():
        print('\t', item)

######################################################################
######################################################################
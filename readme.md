### CLUSTER BROKERS
- `193.167.37.47`

| Description | Endpoint |
| - | -: |
| `Kafka` broker | `:11001`|
| `Cassandra` broker | `:12001`|
| `MLflow` broker | `:5000`|
| `Prometheus` GUI. | [(OPEN LINK)](http://193.167.37.47:9090) `:9090` |
| `Grafana` GUI. | [(OPEN LINK)](http://193.167.37.47:9091) `:9091` |
| Backend FastAPI. | [(OPEN LINK)](http://193.167.37.47:3003) `:3003` |

### GRAFANA DASHBOARDS

| Description | Endpoint |
| - | -: |
| Cadvisor Docker Metrics | [(OPEN LINK)](http://193.167.37.47:9091/d/4dMaCsRZz/cadvisor-docker-metrics) |
| Node Exporter HW Metrics | [(OPEN LINK)](http://193.167.37.47:9091/d/rYdddlPWk/node-exporter-hw-metrics) |
| Kafka Metrics | [(OPEN LINK)](http://193.167.37.47:9091/d/5nhADrDWk/kafka-cluster-metrics) |
| Cassandra DB Metrics | [(OPEN LINK)](http://193.167.37.47:9091/d/000000086/cassandra-cluster-metrics) |

### BACKEND API - CASSANDRA

| Description | Endpoint |
| - | -: |
| `GET` List all keyspaces and tables. | `/cassandra`|
| `GET` List all table structures in keyspace. | `/cassandra/<keyspace>`|
| `GET` List specific table structures. | `/cassandra/<keyspace>/<table>`|
| `POST` Create a new table. | `/cassandra/create`|
| `GET` Initialize default tables from YAML. | `/cassandra/init`|

### BACKEND API - KAFKA

| Description | Endpoint |
| - | -: |
| `GET` List all topic names. | `/kafka`|
| `GET` List details of specific topic. | `/kafka/<topic_name>`|
| `POST` Create a new topic. | `/kafka/create`|
| `GET` Initialize default topics from YAML. | `/kafka/init`|

### BACKEND API - MLFLOW 

| Description | Endpoint |
| - | -: |
| `GET` List created MLflow models & their versions. | `/mlflow`|


### BACKEND API - PIPELINE CONFIG

| Description | Endpoint |
| - | -: |
| `GET` List the global pipeline YAML config. | `/config`|


<style> table { width: 100%; } </style>
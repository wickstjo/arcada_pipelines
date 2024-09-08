<style>
    table {
        width: 100%;
    }
</style>

### CLUSTER BROKERS

| Description | Endpoint |
| - | -: |
| Kafka broker #1 | `localhost:11001`|
| Kafka` broker #2 | `localhost:11002`|
| Cassandra` broker #1 | `localhost:12001`|
| Cassandra` broker #2 | `localhost:12002`|
| `TODO` Flink Job Manager | TODO |
| Prometheus GUI. | `localhost:9090` [(OPEN LINK)](http://localhost:9090)|
| Grafana GUI. | `localhost:9091`  [(OPEN LINK)](http://localhost:9091)|

### GRAFANA DASHBOARDS

| Description | Endpoint |
| - | -: |
| Cadvisor Docker Metrics | [(OPEN LINK)](http://localhost:9091/d/4dMaCsRZz/cadvisor-docker-metrics) |
| Node Exporter HW Metrics | [(OPEN LINK)](http://localhost:9091/d/rYdddlPWk/node-exporter-hw-metrics) |
| Kafka Metrics | [(OPEN LINK)](http://localhost:9091/d/5nhADrDWk/kafka-cluster-metrics) |
| Cassandra DB Metrics | [(OPEN LINK)](http://localhost:9091/d/000000086/cassandra-cluster-metrics) |
| `TODO` Flink Cluster Metrics | TODO |
| `TODO` Custom Model Drift Dashboard | TODO |

### BACKEND API - CASSANDRA

| Description | Endpoint |
| - | -: |
| `GET` List all keyspaces and tables. | `localhost:3003/cassandra`|
| `GET` List all table structures in keyspace. | `localhost:3003/cassandra/<keyspace>`|
| `GET` List specific table structures. | `localhost:3003/cassandra/<keyspace>/<table>`|
| `POST` Create a new table. | `localhost:3003/cassandra/create`|
| `GET` Initialize default tables from YAML. | `localhost:3003/cassandra/init`|

### BACKEND API - KAFKA

| Description | Endpoint |
| - | -: |
| `GET` List all topic names. | `localhost:3003/kafka`|
| `GET` List details of specific topic. | `localhost:3003/kafka/<topic_name>`|
| `POST` Create a new topic. | `localhost:3003/kafka/create`|
| `GET` Initialize default topics from YAML. | `localhost:3003/kafka/init`|

### BACKEND API - PIPELINE CONFIG

| Description | Endpoint |
| - | -: |
| `TODO` List entire latest config YAML. | `localhost:3003/config`|
| `TODO` Update config. | `localhost:3003/config/update`|
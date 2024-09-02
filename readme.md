## PROJECT DOMAINS

- Monitoring Stack:
    - Prometheus: [`localhost:9090`]('localhost:9090)
        - Example endpoint: [`localhost:13000`]('localhost:13000)
    - Grafana: [`localhost:9091`]('localhost:9091)
        - [Cadvisor Docker Metrics](http://localhost:9091/d/4dMaCsRZz/cadvisor-docker-metrics)
        - [Node Exporter HW Metrics](http://localhost:9091/d/rYdddlPWk/node-exporter-hw-metrics)
        - [Kafka Metrics](http://localhost:9091/d/5nhADrDWk/kafka-cluster-metrics)
        - [Cassandra DB Metrics](http://localhost:9091/d/000000086/cassandra-cluster-metrics)
        - Flink Cluster Metrics
        - `TODO: MODEL DRIFT DASHBOARD`
- Kafka Stack:
    - Broker 1: `localhost:11001`
    - Broker 2: `localhost:11002`
- Cassandra Stack:
    - Broker 1: `localhost:12001`
    - Broker 2: `localhost:12002`
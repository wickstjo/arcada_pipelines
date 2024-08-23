package utils

import org.apache.flink.streaming.api.scala.{DataStream}
import org.apache.flink.streaming.connectors.cassandra.{CassandraSink, ClusterBuilder}
import com.datastax.driver.core.{Cluster, PoolingOptions, HostDistance}
import java.net.{InetSocketAddress}

object cassandra_utils {

    // CASSANDRA CONNECTION POOL
    val cassandra_brokers: List[InetSocketAddress] = List(
        new InetSocketAddress("localhost", 12001),
        new InetSocketAddress("localhost", 12002),
    )

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // CREATE A CASSANDAR OUTPUT SINK
    // FOR STREAMS TO FLOW INTO
    def output_sink[T](query_string: String, input_stream: DataStream[T]) = {

        // CREATE THE CLUSTER OUTLINE
        val cluster_pool: ClusterBuilder = new ClusterBuilder() {
            override def buildCluster(builder: Cluster.Builder): Cluster = {

                // CREATE MAX THREAD POOL
                val poolingOptions: PoolingOptions = new PoolingOptions();
                poolingOptions.setMaxConnectionsPerHost(HostDistance.LOCAL, 200);

                builder
                    .addContactPointsWithPorts(cassandra_brokers: _*)
                    .withPoolingOptions(poolingOptions)
                    .build()
            }
        }

        // CREATE THE CLUSTER & ATTACH SINK TO STREAM
        CassandraSink
            .addSink(input_stream)
            .setQuery(query_string)
            .setClusterBuilder(cluster_pool)
            .build()
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
}
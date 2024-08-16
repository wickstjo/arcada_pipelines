package utils

import org.apache.flink.streaming.api.scala.{DataStream}
import org.apache.flink.streaming.connectors.cassandra.{CassandraSink, ClusterBuilder}
import com.datastax.driver.core.{Cluster, PoolingOptions, HostDistance}
import com.datastax.oss.driver.api.core.{CqlSession}
import com.datastax.oss.driver.api.core.cql.{BoundStatement, PreparedStatement, BatchStatement, BatchType}
import java.net.{InetSocketAddress}

import org.apache.flink.api.common.functions.{RichFlatMapFunction, FlatMapFunction}
import org.apache.flink.configuration.{Configuration}
import org.apache.flink.util.{Collector}

import java.util.{ArrayList, Collection}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// import utils.{topo_utils}

object cassandra_utils {

    // class vector_sink (val query_string: String) extends RichFlatMapFunction[Tuple3[String, String, topo_utils.JAVA_VECTOR], Boolean] {

    //     // SERVERSE SPOT FOR ACCUMULATOR DS
    //     private var session: CqlSession = _
    //     private var prepared_statement: PreparedStatement = _

    //     // CONSTRUCTOR
    //     override def open(parameters: Configuration): Unit = {

    //         val cassandra_machines: List[Int] = List(204, 218, 163)

    //         // CREATE AND FILL CASSANDRA CLUSTER CONNECTIONS
    //         val cassandra_endpoints: Collection[InetSocketAddress] = new ArrayList[InetSocketAddress]()

    //         cassandra_machines.foreach(
    //             ip_suffix => cassandra_endpoints.add(
    //                 new InetSocketAddress("192.168.1." + ip_suffix, 9042)
    //             )
    //         )

    //         // CREATE CASSANDRA SESSION
    //         session = CqlSession.builder()
    //             .addContactPoints(cassandra_endpoints)
    //             .withLocalDatacenter("DATACENTER1")
    //             .build()

    //         // CREATE REUSABLE QUERY STATEMENT
    //         prepared_statement = session.prepare(query_string)
    //     }

    //     override def flatMap(input_data: Tuple3[String, String, topo_utils.JAVA_VECTOR], out: Collector[Boolean]): Unit = {
    //         val bound_statement = prepared_statement.bind(input_data._1, input_data._2, input_data._3)
    //         session.executeAsync(bound_statement)
    //     }
    // }

    // class defect_sink (val query_string: String) extends RichFlatMapFunction[topo_utils.DEFECT_INGEST_FORM, Boolean] {

    //     // SERVERSE SPOT FOR ACCUMULATOR DS
    //     private var session: CqlSession = _
    //     private var prepared_statement: PreparedStatement = _

    //     // CONSTRUCTOR
    //     override def open(parameters: Configuration): Unit = {

    //         // ALL CASSANDRA BROKERS
    //         val cassandra_machines: List[Int] = List(204, 218, 163, 149)
    //         val brokers: List[InetSocketAddress] = cassandra_machines.map(
    //             ip_suffix => new InetSocketAddress("192.168.1." + ip_suffix, 12000)
    //         )

    //         // val brokers = List(
    //         //     new InetSocketAddress("192.168.1.163", 12000),
    //         //     new InetSocketAddress("192.168.1.149", 12000)
    //         // )

    //         // SPREAD BROKER CONNECTIONS EVENLY
    //         val runtime_context = getRuntimeContext
    //         val nth_task_replica = runtime_context.getIndexOfThisSubtask
    //         val nth_broker = brokers(nth_task_replica % brokers.length)

    //         // CREATE CASSANDRA SESSION
    //         session = CqlSession.builder()
    //             .addContactPoint(nth_broker)
    //             .withLocalDatacenter("DATACENTER1")
    //             .build()

    //         // CREATE REUSABLE QUERY STATEMENT
    //         prepared_statement = session.prepare(query_string)
    //     }

    //     override def flatMap(input_data: topo_utils.DEFECT_INGEST_FORM, out: Collector[Boolean]): Unit = {
    //         val bound_statement = prepared_statement.bind(
    //             input_data._1,
    //             input_data._2, 
    //             input_data._3, 
    //             input_data._4.asInstanceOf[java.lang.Double], 
    //             input_data._5.asInstanceOf[java.lang.Double], 
    //             input_data._6.asInstanceOf[java.lang.Double], 
    //             input_data._7.asInstanceOf[java.lang.Double], 
    //             input_data._8.asInstanceOf[java.lang.Integer]
    //         )
    //         session.executeAsync(bound_statement)

    //     }
    // }


    // // INJECT IN BATCHES
    // class batch_injection_sink(
    //     val query_string: String,
    //     val batch_size: Int
    // ) extends RichFlatMapFunction[Tuple3[String, String, topo_utils.JAVA_VECTOR], Boolean] {

    //     // SERVERSE SPOT FOR ACCUMULATOR DS
    //     private var session: CqlSession = _
    //     private var prepared_statement: PreparedStatement = _
    //     private var batch_statement: BatchStatement = _
    //     private var current_size: Int = _

    //     // CONSTRUCTOR
    //     override def open(parameters: Configuration): Unit = {

    //         // ALL CASSANDRA BROKERS
    //         val brokers = List(
    //             new InetSocketAddress("192.168.1.163", 12000),
    //             new InetSocketAddress("192.168.1.149", 12000)
    //         )

    //         // SPREAD BROKER CONNECTIONS EVENLY
    //         val runtime_context = getRuntimeContext
    //         val nth_task_replica = runtime_context.getIndexOfThisSubtask
    //         val nth_broker = brokers(nth_task_replica % brokers.length)

    //         // CREATE CASSANDRA SESSION
    //         session = CqlSession.builder()
    //             .addContactPoint(nth_broker)
    //             .withLocalDatacenter("DATACENTER1")
    //             .build()

    //         // CREATE REUSABLE PREPARED & BATCH STATEMENT
    //         prepared_statement = session.prepare(query_string)
    //         batch_statement = BatchStatement.newInstance(BatchType.LOGGED)
    //         current_size = 0
    //     }

    //     override def flatMap(input_data: Tuple3[String, String, topo_utils.JAVA_VECTOR], out: Collector[Boolean]): Unit = {

    //         // PUSH IN VALUE TO BATCH
    //         val bound_statement = prepared_statement.bind(input_data._1, input_data._2, input_data._3)
    //         batch_statement.add(bound_statement)
    //         current_size += 1

    //         // WHEN A FULL BATCH HAS BEEN COLLECTED
    //         if (current_size >= batch_size) {
    //             session.executeAsync(batch_statement)
    //             batch_statement.clear()
    //             println("INJECTED BATCH")
    //             current_size = 0
    //         }
    //     }
    // }

    // // CASSANDRA CONNECTION POOL
    // // val cassandra_brokers: List[InetSocketAddress] = List(
    // //     new InetSocketAddress("192.168.1.163", 12001),
    // //     new InetSocketAddress("192.168.1.163", 12002),
    // //     new InetSocketAddress("192.168.1.163", 12003),
    // //     new InetSocketAddress("192.168.1.163", 12004),

    // //     // new InetSocketAddress("192.168.1.163", 12000),
    // //     // new InetSocketAddress("192.168.1.149", 12000),

    // //     // new InetSocketAddress("192.168.1.218", 12005),
    // //     // new InetSocketAddress("192.168.1.218", 12006),
    // //     // new InetSocketAddress("192.168.1.218", 12007),
    // //     // new InetSocketAddress("192.168.1.218", 12008),
    // // )

    // // val cassandra_brokers: List[InetSocketAddress] = List(
    // //     new InetSocketAddress("localhost", 12001),
    // //     new InetSocketAddress("localhost", 12002),
    // //     new InetSocketAddress("localhost", 12003),
    // // )

    // // val cassandra_brokers: List[InetSocketAddress] = List(
    // //     new InetSocketAddress("cassandra_1", 9042),
    // //     new InetSocketAddress("cassandra_2", 9042),
    // //     new InetSocketAddress("cassandra_3", 9042),
    // // )

    // // CREATE AN KAFKA STREAM OUTPUT
    // def output_sink[T](query_string: String, input_stream: DataStream[T]) = {

    //     // CREATE THE CLUSTER OUTLINE
    //     val cluster_pool: ClusterBuilder = new ClusterBuilder() {
    //         override def buildCluster(builder: Cluster.Builder): Cluster = {

    //             // CREATE MAX THREAD POOL
    //             val poolingOptions: PoolingOptions = new PoolingOptions();
    //             poolingOptions.setMaxConnectionsPerHost(HostDistance.LOCAL, 200);

    //             builder
    //                 .addContactPointsWithPorts(
    //                     new InetSocketAddress("192.168.1.163", 12001),
    //                     new InetSocketAddress("192.168.1.163", 12002),
    //                     new InetSocketAddress("192.168.1.163", 12003),
    //                     new InetSocketAddress("192.168.1.163", 12004)
    //                 )
    //                 .withPoolingOptions(poolingOptions)
    //                 // .addContactPointsWithPorts(new InetSocketAddress("192.168.1.218", 12001))
    //                 // .addContactPointsWithPorts(new InetSocketAddress("cassandra_1", 9042))
    //                 // .addContactPointsWithPorts(new InetSocketAddress("localhost", 12001))
    //                 .build()
    //         }
    //     }

    //     // CREATE THE CLUSTER & ATTACH SINK TO STREAM
    //     CassandraSink.addSink(input_stream)
    //         // .setQuery("INSERT INTO example.wordcount(word, count) values (?, ?);")
    //         .setQuery(query_string)
    //         .setClusterBuilder(cluster_pool)
    //         .build()
    // }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
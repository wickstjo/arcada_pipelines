import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.connectors.cassandra.{CassandraSink, ClusterBuilder}
import com.datastax.oss.driver.api.core.CqlSession
import collection.JavaConverters._

case class Person(name: String, age: Int)

object KafkaToFlinkToCassandraJob {
    def main(args: Array[String]): Unit = {

        // Set up the execution environment
        val env = StreamExecutionEnvironment.getExecutionEnvironment

        // Set up the Kafka consumer
        val kafkaProps = new Properties()
        kafkaProps.setProperty("bootstrap.servers", "kafka_host:9092")
        kafkaProps.setProperty("group.id", "my_group")
        val kafkaConsumer = new FlinkKafkaConsumer[String]("my_topic", new SimpleStringSchema(), kafkaProps)

        // Add the Kafka consumer as a source
        val stream = env.addSource(kafkaConsumer)

        // Parse the input data into a case class
        val parsedStream = stream.map(line => {
            val Array(name, age) = line.split(",")
            Person(name, age.toInt)
        })

        // Define a custom ClusterBuilder class that implements the interface
        class MyClusterBuilder extends ClusterBuilder {
            override def buildCluster(builder: CqlSession.Builder): CqlSession.Builder = {
                // Configure the CqlSession.Builder with your Cassandra cluster settings
                builder
                    .withKeyspace("my_keyspace")
                    .addContactPoint(new InetSocketAddress("localhost", 12001))
                    .addContactPoint(new InetSocketAddress("localhost", 12002))
                    .addContactPoint(new InetSocketAddress("localhost", 12003))
                    .withLocalDatacenter("datacenter1")
            }
        }

        // Create an instance of your custom ClusterBuilder
        val clusterBuilder = new MyClusterBuilder()

        // Write the data into Cassandra using CassandraSink
        CassandraSink.addSink(parsedStream.javaStream)
            .setClusterBuilder(clusterBuilder)
            .setMapperOptions(() => {
                val mapper = new MappingManager(clusterBuilder.getClusterBuilder().build()).mapper(classOf[Person])
                mapper.setDefaultSaveOptions(Mapper.Option.saveNullFields(false))
                mapper
            })
            .build()

        // Execute the job
        env.execute("KafkaToFlinkToCassandraJob")
    }
}
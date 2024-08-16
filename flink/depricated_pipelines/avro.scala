import java.io.File
import java.nio.file.Paths

import org.apache.avro.Schema
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.scala.extensions._
import org.apache.flink.streaming.connectors.kafka.KafkaDeserializationSchema
import org.apache.flink.streaming.connectors.kafka.KafkaSource
import org.apache.flink.streaming.connectors.kafka.KafkaSourceBuilder
import org.apache.flink.streaming.connectors.kafka.config.StartupMode
import org.apache.flink.streaming.connectors.kafka.internals.KafkaTopicPartition
import org.apache.flink.streaming.util.serialization.SimpleStringSchema

object KafkaAvroDeserializerJob {
    def main(args: Array[String]): Unit = {
        val env = StreamExecutionEnvironment.getExecutionEnvironment

        // Set up Kafka consumer properties
        val kafkaProps = new Properties()
        kafkaProps.setProperty("bootstrap.servers", "localhost:9092")
        kafkaProps.setProperty("group.id", "myGroup")

        // Set up Avro schema
        val schemaPath = Paths.get("path/to/avro/schema/file.avsc").toAbsolutePath.toString
        val schema: Schema = new Schema.Parser().parse(new File(schemaPath))

        // Create a Kafka source that reads from a topic and uses Avro deserialization
        val kafkaSource: KafkaSource[String] = KafkaSourceBuilder
            .newBuilder(new SimpleStringSchema())
            .setTopics(Set("myTopic"))
            .setProperties(kafkaProps)
            .setStartupMode(StartupMode.LATEST)
            .setDeserializer(new AvroDeserializationSchema(schema))
            .build()

        // Create a Flink data stream that reads from the Kafka source
        val kafkaStream = env.fromSource(kafkaSource, "Kafka Avro Source")

        // Print the data to stdout for debugging
        kafkaStream.print()

        env.execute("Kafka Avro Deserializer Job")
    }

    class AvroDeserializationSchema(schema: Schema) extends KafkaDeserializationSchema[String] {
        override def deserialize(record: ConsumerRecord[Array[Byte], Array[Byte]]): String = {
            // Deserialize the Avro message
            val decoder = DecoderFactory.get().binaryDecoder(record.value(), null)
            val reader = new GenericDatumReader[GenericRecord](schema)
            val avroRecord = reader.read(null, decoder)

            // Return the record as a JSON string
            avroRecord.toString
        }

        override def getProducedType: TypeInformation[String] = TypeInformation.of(classOf[String])
        override def getTopics: util.List[String] = util.Arrays.asList("myTopic")
        override def getWatermarkStrategy: WatermarkStrategy[String] = WatermarkStrategy.noWatermarks()
        override def getPartitionDiscoverer: KafkaPartitionDiscoverer = new KafkaTopicPartitionDiscoverer(kafkaProps, getTopics, null)
    }

    class KafkaTopicPartitionDiscoverer(properties: Properties, topics: util.List[String], kafkaPartitionAssigner: KafkaPartitionAssigner) extends KafkaPartitionDiscoverer(properties, topics, kafkaPartitionAssigner) {
        override def getKafkaPartitions(topics: util.List[String]): util.List[KafkaTopicPartition] = {
            // Override the Kafka partition discovery logic to always return an empty list,
            // since the KafkaSourceBuilder has already set the partitions for us
            util.Collections.emptyList[KafkaTopicPartition]
        }
    }
}

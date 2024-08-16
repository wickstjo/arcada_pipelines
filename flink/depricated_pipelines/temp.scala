import java.util.Properties

import io.confluent.kafka.serializers.{AbstractKafkaSchemaSerDeConfig, ConfluentRegistryAvroDeserializationSchema, KafkaAvroDeserializer, KafkaAvroDeserializerConfig}
import io.confluent.kafka.serializers.subject.TopicRecordNameStrategy
import org.apache.avro.generic.GenericRecord

import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.functions.source.SourceFunction
import org.apache.flink.streaming.connectors.kafka.KafkaSource

object KafkaFlinkJob {
  def main(args: Array[String]): Unit = {
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // Set up Avro deserialization properties
    val deserializationProps = new Properties()
    deserializationProps.setProperty(AbstractKafkaSchemaSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, "http://localhost:8081")
    deserializationProps.setProperty(KafkaAvroDeserializerConfig.SPECIFIC_AVRO_READER_CONFIG, "false")
    deserializationProps.setProperty(KafkaAvroDeserializerConfig.VALUE_SUBJECT_NAME_STRATEGY, classOf[TopicRecordNameStrategy].getName)

    // Create a Kafka source builder
    val kafkaSourceBuilder = KafkaSource.builder[GenericRecord]()
      .setBootstrapServers("localhost:9092")
      .setGroupId("test-group")
      .setTopics("test-topic")
      .setDeserializer(new ConfluentRegistryAvroDeserializationSchema[GenericRecord](classOf[GenericRecord], deserializationProps))
      .setProperty("schema.registry.url", "http://localhost:8081")
      .setProperty("specific.avro.reader", "false")
      .setProperty("value.subject.name.strategy", classOf[TopicRecordNameStrategy].getName)

    // Create a source function from the Kafka source builder
    val kafkaSource: SourceFunction[GenericRecord] = kafkaSourceBuilder.build()

    // Add the Kafka source function as a data source to the Flink streaming job
    val stream = env.addSource(kafkaSource)

    // Print the received data
    stream.print()

    // Execute the Flink streaming job
    env.execute("Kafka Flink Job")
  }
}
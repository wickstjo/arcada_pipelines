import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.connectors.kafka.{FlinkKafkaConsumer, FlinkKafkaProducer}
import org.apache.flink.streaming.util.serialization.{AbstractDeserializationSchema, AbstractSerializationSchema}
import org.apache.flink.api.common.serialization.{SerializationSchema, DeserializationSchema}
import org.apache.flink.api.common.functions.MapFunction
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig
import io.confluent.kafka.schemaregistry.client.CachedSchemaRegistryClient
import io.confluent.kafka.schemaregistry.client.rest.RestService
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient
import io.confluent.kafka.serializers.AbstractKafkaAvroSerDeConfig
import org.apache.avro.Schema
import org.apache.avro.generic.GenericRecord

case class MyRecord(field1: String, field2: Int)

object FlinkAvroConfluentRegistryKafkaExample {
    def main(args: Array[String]): Unit = {
        val env = StreamExecutionEnvironment.getExecutionEnvironment

        val schemaRegistryUrl = "http://localhost:8081"
        val kafkaBootstrapServers = "localhost:9092"
        val topic = "my-topic"

        val schemaRegistry = new CachedSchemaRegistryClient(schemaRegistryUrl, 100)
        
        val kafkaAvroDeserializationConfig = Map(
            KafkaAvroDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG -> schemaRegistryUrl,
            KafkaAvroDeserializerConfig.SPECIFIC_AVRO_READER_CONFIG -> true.toString
        )

        val deserializationSchema = new AvroDeserializationSchema[MyRecord](
            classOf[MyRecord], 
            schemaRegistry, 
            kafkaAvroDeserializationConfig
        )

        val kafkaConsumer = new FlinkKafkaConsumer[MyRecord](
            topic, 
            deserializationSchema, 
            kafkaAvroDeserializationConfig
        )

        kafkaConsumer.setStartFromEarliest()

        val stream = env.addSource(kafkaConsumer)
        val processedStream = stream.map(new MyMapFunction)

        processedStream.print()

        env.execute("Flink Avro Confluent Registry Kafka Example")
    }

    class MyMapFunction extends MapFunction[MyRecord, MyRecord] {
        override def map(value: MyRecord): MyRecord = {
            // Process the input record and return the output record
            value
        }
    }

    class AvroDeserializationSchema[T <: GenericRecord](
        val recordClass: Class[T],
        val schemaRegistryClient: SchemaRegistryClient,
        val kafkaAvroDeserializationConfig: Map[String, String]
    ) extends AbstractDeserializationSchema[T] {

        private var schema: Schema = _

        override def deserialize(message: Array[Byte]): T = {
            if (schema == null) {
                schema = schemaRegistryClient.getBySubjectAndId(
                recordClass.getName + "-value",
                schemaRegistryClient.getLatestSchemaMetadata(recordClass.getName + "-value").getId)
            }

            AvroUtils.deserialize(message, schema).asInstanceOf[T]
        }
    }
}
// GENERAL
import org.apache.flink.streaming.api.scala._
import org.apache.flink.api.common.typeinfo.TypeInformation

// KAFKA STUFF
import org.apache.flink.connector.kafka.source.KafkaSource
import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer

// CASSANDRA STUFF
import org.apache.flink.streaming.connectors.cassandra.CassandraSink

// MICROBATCHING
import org.apache.flink.streaming.api.windowing.time.Time

// SERIALIZATION
import org.apache.flink.api.common.serialization.{DeserializationSchema}
import play.api.libs.json.{Json, JsValue}
// import org.apache.flink.api.common.serialization.SimpleStringSchema

// SCHEMA REGISTRY
import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroDeserializationSchema,ConfluentRegistryAvroSerializationSchema}
import org.apache.avro.generic.GenericRecord

// import io.confluent.kafka.{AbstractKafkaSchemaSerDeConfig, KafkaAvroDeserializerConfig, KafkaAvroDeserializer, KafkaAvroDeserializationSchema, KafkaAvroSerializer}
// import io.confluent.kafka.serializers.{AbstractKafkaSchemaSerDeConfig, KafkaAvroDeserializerConfig, KafkaAvroDeserializer, KafkaAvroDeserializationSchema, KafkaAvroSerializer}

// import io.confluent.kafka.serializers.{KafkaAvroDeserializer, KafkaAvroSerializer}
// import io.confluent.common.serialization.AbstractKafkaAvroSerDeConfig

case class MyData(var name: String, age: Int) {
    def update_name(new_name: String): Unit = {
        this.name = new_name
    }
}

class my_deserializer extends DeserializationSchema[MyData] {
    override def deserialize(message: Array[Byte]): MyData = {

        // PARSE THE BYTE ARRAY INTO A JsValue OBJECT
        val stringified = new String(message)

        // ATTEMPT TO PARSE IT AS A JSON-LIKE OBJECT
        try {
            val parsed = Json.parse(stringified)

            // val name = (parsed \ "name").as[String]
            // val age = (parsed \ "age").as[Int]

            return MyData(
                parsed("name").as[String],
                parsed("age").as[Int],
            )

        // CATCH ERRORS SILENTLY
        } catch {
            case _: Throwable => {
                println("COULD NOT PARSE RECEIVED MESSAGE");
                null
            }
        }
    }

    // AUXILLARY METHODS
    override def isEndOfStream(nextElement: MyData): Boolean = false
    override def getProducedType: TypeInformation[MyData] = TypeInformation.of(classOf[MyData])
}

object Main extends App {
    
    // SET TYPEINFO & CREATE THE ENVIRONMENT CONTEXT
    implicit val typeInfo = TypeInformation.of(classOf[(MyData)])
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // TOPIC DETAILS
    val input_topic = "topic1"
    val consumer_group = input_topic + ".flink_consumers"

    // CREATE THE KAFKA INPUT SOURCE
    val kafka_source = KafkaSource.builder()
        // .setBootstrapServers("kafka_broker_1:11000")
        .setBootstrapServers("localhost:10001,localhost:10002,localhost:10003")
        .setTopics(input_topic)
        .setGroupId(consumer_group)
        .setStartingOffsets(OffsetsInitializer.latest())
        // .setValueOnlyDeserializer(new my_deserializer())
        .setValueOnlyDeserializer(ConfluentRegistryAvroDeserializationSchema.forGeneric(classOf[GenericRecord], "http://localhost:8181"))
        .build()

    //////////////////////////////////////////////////////////////////////////
    // TODO: INTEGRATE AVRO SCHEMA REGISTRY
    //////////////////////////////////////////////////////////////////////////

    // RAW KAFKA INPUT STREAM
    val data_stream = env.fromSource(kafka_source, WatermarkStrategy.noWatermarks(), "kafka input")
        .setParallelism(3)

    // FILTER BASED ON AGE
    val filtered_stream = data_stream
        .filter(item => item.age >= 4)
        .name("filtering starge")
        .setParallelism(2)

    // UPDATE NAME PROPERTY
    val transformation_stream = filtered_stream
        .map(item => {
            item.update_name("foobar")
            item
        })
        .name("transformation stage")
        .setParallelism(3)
    
    // GATHER DATA INTO SINK
    val tuple_stream = transformation_stream
        .map(item => (item.name, item.age))
        .name("batch storage stage")
        .setParallelism(2)

        // .timeWindowAll(Time.seconds(10))
        // .window(TumblingProcessingTimeWindows.of(Time.seconds(5)))

    // PUSH DATA TO CASSANDRA
    CassandraSink.addSink(tuple_stream)
        .setHost("localhost", 12001)
        // .setHost("cassandra_1", 9042)
        .setQuery("INSERT INTO example.wordcount(word, count) values (?, ?);")
        .build()

    // PRINT OUT PROCESSED ROWS
    tuple_stream.print()

    // FINALLY, START THE APPLICATION
    env.execute("read from kafka source and dump it into cassandra")
}
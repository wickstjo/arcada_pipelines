// GENERAL
import org.apache.flink.streaming.api.scala._
import org.apache.flink.api.common.typeinfo.TypeInformation

// KAFKA STUFF
import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer

// CASSANDRA STUFF
import org.apache.flink.streaming.connectors.cassandra.CassandraSink

// AVRO SERIALIZATION
import java.io.File
import org.apache.avro.Schema
import org.apache.avro.generic.GenericRecord
import org.apache.flink.formats.avro.AvroDeserializationSchema

import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroDeserializationSchema} // ConfluentRegistryAvroSerializationSchema

object Main extends App {
    
    // SET TYPEINFO & CREATE THE ENVIRONMENT CONTEXT
    // implicit val typeInfo = TypeInformation.of(classOf[(GenericRecord)])
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    // env.getConfig.disableAutoTypeRegistration()
    // var executionConfig = env.getConfig
    // println(executionConfig)

    // TOPIC DETAILS
    val input_topic = "topic1"
    val consumer_group = input_topic + ".flink_consumers"

    // LOAD SCHEMA FROM FILE
    val schema_file = new File("/home/wickstjo/Documents/schemas/fiberline_1.cat2.avro")
    val schema: Schema = new Schema.Parser().parse(schema_file)
    val deserializer = ConfluentRegistryAvroDeserializationSchema.forGeneric(schema, "http://localhost:8181")

    // CREATE THE KAFKA INPUT SOURCE
    val kafka_source = KafkaSource.builder()
        // .setBootstrapServers("kafka_broker_1:11000")
        .setBootstrapServers("localhost:10001,localhost:10002,localhost:10003")
        .setTopics(input_topic)
        .setGroupId(consumer_group)
        .setStartingOffsets(OffsetsInitializer.latest())
        .setValueOnlyDeserializer(deserializer)
        // .setValueOnlyDeserializer(AvroDeserializationSchema.forGeneric(schema))
        // .setValueOnlyDeserializer(new SimpleStringSchema)
        .build()

    // RAW KAFKA INPUT STREAM
    val data_stream = env.fromSource(kafka_source, WatermarkStrategy.noWatermarks(), "kafka input")
        .print()

    //     .setParallelism(3)

    // // FILTER BASED ON AGE
    // val filtered_stream = data_stream
    //     .filter(item => item.age >= 4)
    //     .name("filtering starge")
    //     .setParallelism(2)

    // // UPDATE NAME PROPERTY
    // val transformation_stream = filtered_stream
    //     .map(item => {
    //         item.update_name("foobar")
    //         item
    //     })
    //     .name("transformation stage")
    //     .setParallelism(3)
    
    // // GATHER DATA INTO SINK
    // val tuple_stream = transformation_stream
    //     .map(item => (item.name, item.age))
    //     .name("batch storage stage")
    //     .setParallelism(2)

    //     // .timeWindowAll(Time.seconds(10))
    //     // .window(TumblingProcessingTimeWindows.of(Time.seconds(5)))

    // // PUSH DATA TO CASSANDRA
    // CassandraSink.addSink(tuple_stream)
    //     .setHost("localhost", 12001)
    //     // .setHost("cassandra_1", 9042)
    //     .setQuery("INSERT INTO example.wordcount(word, count) values (?, ?);")
    //     .build()

    // // PRINT OUT PROCESSED ROWS
    // tuple_stream.print()

    // FINALLY, START THE APPLICATION
    env.execute("read from kafka source and dump it into cassandra")
}
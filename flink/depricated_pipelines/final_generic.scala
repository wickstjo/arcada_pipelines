import org.apache.flink.streaming.api.scala._
import scala.io.Source
import org.apache.avro.Schema
import org.apache.avro.generic.{GenericRecord, GenericData}

import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.connector.kafka.sink.{KafkaSink, KafkaRecordSerializationSchema}
import org.apache.flink.formats.avro.{AvroSerializationSchema}

// import org.apache.flink.formats.avro.typeutils.{GenericRecordAvroTypeInfo}
// import org.apache.flink.api.common.typeinfo.{TypeInformation}

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    // env.getConfig.registerKryoType(classOf[GenericData])
    // env.getConfig.registerKryoType(classOf[GenericRecord])

    // LOAD AVRO SCHEMA FROM FILE
    val schema_str: String = Source.fromFile("/home/wickstjo/Documents/schemas/fiberline_1.cat2.avro").getLines.mkString
    val schema: Schema = new Schema.Parser().parse(schema_str)

    // CREATE SCHEMA WRAPPERS
    val sink_serializer: AvroSerializationSchema[GenericRecord] = AvroSerializationSchema.forGeneric(schema)
    val temp_record: GenericRecord = new GenericData.Record(schema)

    // CREATE INPUT STREAM
    val input_stream = env.fromCollection(Array(
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
        (7.0, 8.0, 9.0),
    ))
    
    // CONVERT TUPLE TO GENERIC RECORD
    val conversion_stream = input_stream.map(item => {
        temp_record.put("MotorSpeedMe", item._1)
        temp_record.put("MotorTorqMe", item._2)
        temp_record.put("SpeedAs", item._3)

        temp_record
    })

    // SERIALIZE & PUSH RECORDS TO KAFKA
    val output_sink: KafkaSink[GenericRecord] = KafkaSink.builder()
        .setBootstrapServers("localhost:10001,localhost:10002,localhost:10003")
        .setRecordSerializer(
            KafkaRecordSerializationSchema.builder()
                .setTopic("topic1")
                .setValueSerializationSchema(sink_serializer)
                .build()
        )
        .build()
    
    // ATTACH CONVERSION STREAM WITH SINK
    conversion_stream.sinkTo(output_sink)

    // FINALLY, START THE APPLICATION
    env.execute("foobar")
}
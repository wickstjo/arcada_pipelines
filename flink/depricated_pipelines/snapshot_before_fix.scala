import org.apache.flink.streaming.api.scala._
import scala.io.Source
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.{GenericRecord, GenericData}

import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.connector.kafka.sink.{KafkaSink, KafkaRecordSerializationSchema}
import org.apache.flink.formats.avro.{AvroSerializationSchema}

import org.apache.flink.formats.avro.typeutils.{GenericRecordAvroTypeInfo}
import org.apache.flink.api.common.typeinfo.{TypeInformation}

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.getConfig.registerKryoType(classOf[GenericData])
    env.getConfig.registerKryoType(classOf[GenericRecord])

    // LOAD AVRO SCHEMA FROM FILE
    val schema_str: String = Source.fromFile("/home/wickstjo/Documents/schemas/fiberline_1.cat2.avro").getLines.mkString
    val schema: Schema = new Schema.Parser().parse(schema_str)
    val sink_serializer = AvroSerializationSchema.forGeneric(schema)

    // MOCK DATA FOR INPUT STREAM
    val data = Array(
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
        (7.0, 8.0, 9.0),
    )

    // CREATE INPUT STREAM
    val input_stream: DataStream[GenericRecord] = env.fromCollection(data).map(item => {

        // CONVERT TUPLE TO GENERIC RECORD
        val genericRecord: GenericRecord = new GenericData.Record(schema)
        genericRecord.put("MotorSpeedMe", item._1)
        genericRecord.put("MotorTorqMe", item._2)
        genericRecord.put("SpeedAs", item._3)

        genericRecord
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
    
    // ATTACH INPUT STREAM WITH SINK
    input_stream.sinkTo(output_sink)

    // FINALLY, START THE APPLICATION
    env.execute("foobar")
}
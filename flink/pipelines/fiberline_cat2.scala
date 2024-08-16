package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._
import org.apache.avro.specific.{SpecificRecordBase}

// KAFKA SOURCE
import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.connector.kafka.source.enumerator.initializer.{OffsetsInitializer}
import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroSerializationSchema}
import org.apache.flink.api.common.eventtime.{WatermarkStrategy}

// KAFKA SINK
import org.apache.flink.connector.kafka.sink.{KafkaSink, KafkaRecordSerializationSchema}
import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroDeserializationSchema}

// SCHEMAS
import schemas.fiberline_1.{cat_2 => Cat2}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // START PIPING DATA INTO THE SYSTEM
    val input_stream: DataStream[(Float, Float, Float)] = env.fromCollection(Array(
        (1.0f, 2.0f, 3.0f),
        (4.0f, 5.0f, 6.0f),
        (7.0f, 8.0f, 9.0f),
    ))

    // CONVERT TUPLE TO GENERIC RECORD
    val conversion_stream: DataStream[Cat2] = input_stream.map(item => {
        new Cat2(item._1, item._2, item._3)
    })

    // KAFKA INPUT TOPIC
    val kafka_topic: String = "fiberline_1.cat_2"
    val data_schema = classOf[Cat2]

    // CREATE OUTPUT SINK & ATTACH PREV STREAM TO IT
    val kafka_sink: KafkaSink[Cat2] = kafka_utils.output_sink(kafka_topic, data_schema)
    conversion_stream.sinkTo(kafka_sink)

    // CREATE THE KAFKA INPUT SOURCE & ATTACH IT TO ENV
    val kafka_source: KafkaSource[Cat2] = kafka_utils.input_source(kafka_topic, data_schema)
    val data_stream = env.fromSource(kafka_source, WatermarkStrategy.noWatermarks(), kafka_topic + " input source")

    data_stream.print()

    // FINALLY, START THE APPLICATION
    env.execute("HDF5 => kafka => cassandra pipeline")
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

object kafka_utils {

    // KAFKA API ENDPOINTS
    val kafka_brokers: String = "localhost:10001,localhost:10002,localhost:10003"
    val schema_registry: String = "http://localhost:8181"

    // CREATE THE KAFKA INPUT SOURCE
    def input_source [T <: SpecificRecordBase] (kafka_topic: String, avro_class: Class[T]): KafkaSource[T] = {

        // CREATE THE RECORD DESERIALIZER
        val deserializer = ConfluentRegistryAvroDeserializationSchema.forSpecific(
            avro_class, 
            this.schema_registry
        )

        // CREATE & RETURN THE INPUT SOURCE
        return KafkaSource.builder()
            .setBootstrapServers(this.kafka_brokers)
            .setTopics(kafka_topic)
            .setGroupId(kafka_topic + "_consumers")
            .setStartingOffsets(OffsetsInitializer.latest())
            .setValueOnlyDeserializer(deserializer)
            .build()
    }

    // CREATE AN KAFKA STREAM OUTPUT
    def output_sink [T <: SpecificRecordBase] (kafka_topic: String, avro_class: Class[T]): KafkaSink[T] = {

        // CREATE THE RECORD SERIALIZER
        val sink_serializer = ConfluentRegistryAvroSerializationSchema.forSpecific(
            avro_class, 
            kafka_topic, 
            this.schema_registry
        )

        // CREATE & RETURN THE OUTPUT STREAM
        return KafkaSink.builder()
            .setBootstrapServers(this.kafka_brokers)
            .setRecordSerializer(
                KafkaRecordSerializationSchema.builder()
                    .setTopic(kafka_topic)
                    .setValueSerializationSchema(sink_serializer)
                    .build()
            )
            .build()
    }
}
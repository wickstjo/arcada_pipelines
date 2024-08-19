package utils

import org.apache.flink.streaming.api.scala._

import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.connector.kafka.source.KafkaSource
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer
import scala.reflect.{ClassTag}
import org.apache.flink.api.common.serialization.DeserializationSchema

// import org.apache.flink.api.common.serialization.SimpleStringSchema

object kafka_utils {

    // YOUR KAFKA BROKERS
    val kafka_brokers: String = "localhost:11001,localhost:11002"

    // CREATE A KAFKA INPUT SOURCE
    def input_source [SCHEMA, DESERIALIZER <: DeserializationSchema[SCHEMA]] (
        kafka_topic: String,
    )(implicit ct: ClassTag[SCHEMA], schema_ct: ClassTag[DESERIALIZER]): (KafkaSource[SCHEMA], WatermarkStrategy[SCHEMA], String) = {

        // CREATE CLARIFYING NAMES
        val consumer_group: String = kafka_topic + "_consumers"
        val source_name: String = kafka_topic + "_kafka"

        // DEFINE THE KAFKA SOURCE
        val kafka_source = KafkaSource.builder[SCHEMA]()
            .setBootstrapServers(kafka_brokers)
            .setTopics(kafka_topic)
            .setGroupId(consumer_group)
            .setStartingOffsets(OffsetsInitializer.earliest())
            // .setStartingOffsets(OffsetsInitializer.latest())
            .setValueOnlyDeserializer(schema_ct.runtimeClass.getDeclaredConstructor().newInstance().asInstanceOf[DESERIALIZER])
            .build()

        // CREATE THE TIMESTAMP STRATEGY
        val timestamp_strategy: WatermarkStrategy[SCHEMA] = WatermarkStrategy.noWatermarks()

        return (kafka_source, timestamp_strategy, source_name)
    }

    // // CREATE AN KAFKA STREAM OUTPUT
    // def output_sink [T <: SpecificRecordBase] (kafka_topic: String, input_stream: DataStream[T])(implicit ct: ClassTag[T]): Unit = {

    //     // CREATE THE RECORD SERIALIZER
    //     val sink_serializer =  KafkaRecordSerializationSchema.builder()
    //         .setTopic(kafka_topic)
    //         .setValueSerializationSchema(
    //             ConfluentRegistryAvroSerializationSchema.forSpecific(
    //                 ct.runtimeClass.asInstanceOf[Class[T]],
    //                 kafka_topic, 
    //                 schema_registry
    //             )
    //         )
    //         .build()

    //     // CREATE & RETURN THE OUTPUT STREAM
    //     val sink = KafkaSink.builder[T]()
    //         .setBootstrapServers(kafka_brokers)
    //         .setRecordSerializer(sink_serializer)
    //         .build()

    //     input_stream.sinkTo(sink)
    // }
}
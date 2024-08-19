package utils

// SHARED
import org.apache.flink.streaming.api.scala._
import org.apache.avro.specific.{SpecificRecordBase}
import scala.reflect.{ClassTag}

// KAFKA SOURCE
import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.connector.kafka.source.enumerator.initializer.{OffsetsInitializer}
import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroSerializationSchema}

// KAFKA SINK
import org.apache.flink.connector.kafka.sink.{KafkaSink, KafkaRecordSerializationSchema}
import org.apache.flink.formats.avro.registry.confluent.{ConfluentRegistryAvroDeserializationSchema}

// FLINK TIMESTAMPS
import org.apache.flink.api.common.eventtime.{WatermarkStrategy}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

object kafka_utils {

    // SERVICE ENDPOINTS
    val schema_registry: String = "http://192.168.1.24:8181"
    val kafka_machines: List[Int] = List(24) // 204, 218, 163, 149

    val kafka_brokers: String = kafka_machines.map(
        ip_suffix => "192.168.1." + ip_suffix + ":9092"
    ).mkString(",")

    // CREATE THE KAFKA INPUT SOURCE
    def input_source [T <: SpecificRecordBase] (kafka_topic: String)(implicit ct: ClassTag[T]): (KafkaSource[T], WatermarkStrategy[T], String) = {

        // CREATE THE RECORD DESERIALIZER
        val deserializer = ConfluentRegistryAvroDeserializationSchema.forSpecific[T](
            ct.runtimeClass.asInstanceOf[Class[T]],
            this.schema_registry
        )

        // CREATE CLARIFYING NAMES
        val consumer_group: String = kafka_topic + "_consumers"
        val source_name: String = kafka_topic + "_kafka"

        // CREATE THE KAFKA SOURCE
        val kafka_source: KafkaSource[T] = KafkaSource.builder()
            .setBootstrapServers(this.kafka_brokers)
            .setTopics(kafka_topic)
            .setGroupId(consumer_group)
            .setStartingOffsets(OffsetsInitializer.latest())
            .setValueOnlyDeserializer(deserializer)
            .build()

        // CREATE THE TIMESTAMP STRATEGY
        val timestamp_strategy: WatermarkStrategy[T] = WatermarkStrategy.noWatermarks()

        // RETURN PROPERTIES
        return (kafka_source, timestamp_strategy, source_name)
    }

    // CREATE AN KAFKA STREAM OUTPUT
    def output_sink [T <: SpecificRecordBase] (kafka_topic: String, input_stream: DataStream[T])(implicit ct: ClassTag[T]): Unit = {

        // CREATE THE RECORD SERIALIZER
        val sink_serializer =  KafkaRecordSerializationSchema.builder()
            .setTopic(kafka_topic)
            .setValueSerializationSchema(
                ConfluentRegistryAvroSerializationSchema.forSpecific(
                    ct.runtimeClass.asInstanceOf[Class[T]],
                    kafka_topic, 
                    schema_registry
                )
            )
            .build()

        // CREATE & RETURN THE OUTPUT STREAM
        val sink = KafkaSink.builder[T]()
            .setBootstrapServers(kafka_brokers)
            .setRecordSerializer(sink_serializer)
            .build()

        input_stream.sinkTo(sink)
    }
}
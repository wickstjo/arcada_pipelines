package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._
import org.apache.flink.connector.kafka.source.{KafkaSource}
import org.apache.flink.connector.kafka.sink.{KafkaSink}

// PROCESSING
import org.apache.flink.api.common.eventtime.{WatermarkStrategy}
import org.apache.flink.streaming.api.windowing.time.{Time}
import org.apache.flink.streaming.api.windowing.assigners.{TumblingProcessingTimeWindows, SlidingProcessingTimeWindows, EventTimeSessionWindows, ProcessingTimeSessionWindows}

// SCHEMAS
import schemas.surface_data.{sensor_1A => SensorData}

// CUSTOM
import utils.{kafka_utils}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // KAFKA INPUT
    val kafka_topic: String = "surface_data.sensor_1A"
    val data_schema: Class[SensorData] = classOf[SensorData]
    val timestamp_strat: WatermarkStrategy[SensorData] = WatermarkStrategy.noWatermarks()

    // CREATE THE KAFKA INPUT SOURCE & ATTACH IT TO ENV
    val kafka_source: KafkaSource[SensorData] = kafka_utils.input_source(kafka_topic, data_schema)
    val data_stream: DataStream[SensorData] = env.fromSource(kafka_source, timestamp_strat, "kafka source: " + kafka_topic)

    val batched_stream = data_stream
        .keyBy(item => item.get(0))
        .window(TumblingProcessingTimeWindows.of(Time.seconds(1)))

    data_stream.print()

    // FINALLY, START THE APPLICATION
    env.execute("surface sensor_1A HDF5 ingestion")
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
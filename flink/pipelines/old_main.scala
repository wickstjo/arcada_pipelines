package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._

// PROCESSING
import org.apache.flink.streaming.api.windowing.time.{Time}
import org.apache.flink.streaming.api.windowing.assigners.{TumblingProcessingTimeWindows, SlidingProcessingTimeWindows, EventTimeSessionWindows, ProcessingTimeSessionWindows}

// CUSTOM MODULES & SCHEMAS
import utils.{kafka_utils, cassandra_utils}
import schemas.surface_data.{sensor_1A => Sensor_schema}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // KAFKA INPUT DETAILS
    val kafka_topic = "surface_data.sensor_1A"
    val input_schema = classOf[Sensor_schema]

    // CREATE THE KAFKA SOURCE
    val (kafka_source, timestamp_strat, source_name) = kafka_utils.input_source(kafka_topic, input_schema)
    val input_stream: DataStream[Sensor_schema] = env.fromSource(kafka_source, timestamp_strat, source_name)

    // val batched_stream = data_stream
    //     .keyBy(item => item.get(0))
    //     .window(TumblingProcessingTimeWindows.of(Time.seconds(1)))

    // input_stream.print()1

    // CONVERT STRUCTS TO TUPLES FOR INJECTION
    val tuple_stream = input_stream
        .map(item => (
            item.getTimestamp().toString(),
            item.getSerialNumber().toString(),
            item.getDatapoints()
        ))
        .name("pre-injection formatting")
        .setParallelism(1)
    
    // tuple_stream.print()

    // // CREATE FINAL OUTPUT SINK & ATTACH TUPLE STREAM TO IT
    val query_string = "INSERT INTO surface_data.sensor_4a (timestamp, serial_number, datapoints) values (?, ?, ?);"
    val output_sink = cassandra_utils.output_sink(query_string, tuple_stream)

    // FINALLY, NAME & START THE APPLICATION
    env.execute("surface sensor_1A HDF5 ingestion")
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
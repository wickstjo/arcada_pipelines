package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._
import utils.{kafka_utils, cassandra_utils, other_utils}
import schemas.surface_data.{sensor_1A => Sensor_schema}

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    // CREATE THE SLIDING WINDOW ACCUMULATOR
    val accumulator = new other_utils.sliding_window_accumulator[Int] (
        window_size=5,
        slide_by=2
    )

    // START PIPING DATA INTO THE SYSTEM
    val input_stream = env.fromCollection(Array(
        1, 2, 3, 4, 5,
        6, 7, 8, 9, 10,
        11, 12, 13, 14, 15,
        16, 17, 18, 19, 20
    ))

    // // KAFKA INPUT DETAILS
    // val kafka_topic = "surface_data.sensor_1A"
    // val input_schema = classOf[Sensor_schema]

    // // CREATE THE KAFKA SOURCE
    // val (kafka_source, timestamp_strat, source_name) = kafka_utils.input_source(kafka_topic, input_schema)
    // val input_stream: DataStream[Sensor_schema] = env.fromSource(kafka_source, timestamp_strat, source_name)

    // GATHER EVENTS INTO WINDOW
    val accumulator_stream = input_stream
        .map(item => accumulator.add_event(item))
        .name("SLIDING WINDOW ACCUMULATOR")
        .setParallelism(1)

    // FILTER OUT INCOMPLETE WINDOWS
    val sliding_window_stream = accumulator_stream
        .filter(item => item != null)
        .name("WINDOW LENGTH FILTERING")
        .setParallelism(1)

    val output = sliding_window_stream
        .print()
        .setParallelism(1)

    // FINALLY, START THE APPLICATION
    env.execute("1A TOPO PROCESSING PIPELINE")
}
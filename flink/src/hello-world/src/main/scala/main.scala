package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._
import scala.collection.JavaConverters._

// import utils.{kafka_utils, cassandra_utils, topo_utils}
import schemas.surface_data.{sensor_1A => SENSOR_SCHEMA, defective_tile => DEFECT_SCHEMA}
import utils.{kafka_utils, cassandra_utils, topo_utils}

import org.apache.flink.configuration.Configuration

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

    // env.setRestartStrategy(
    //     RestartStrategies.fixedDelayRestart(
    //         maxAttempts = 0, // Disable restarts
    //         delayBetweenAttempts = 0 // No delay between restart attempts
    //     )
    // )

    // USE REGULAR KEY-VALUE CHECKPOINTING -- IN MILLISECONDS
    env.enableCheckpointing(1000)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // TENSOR DIMENSIONS
    val vector_length: Int = 800
    val matrix_height: Int = 224
    val tensor_depth: Int = 3

    // OVERLAP CONFIG
    val large_tile_overlap: Int = 40
    val adjusted_matrix_height: Int = matrix_height - large_tile_overlap

    // TILE CONFIGS
    val n_mini_tiles: Int = 18

    // ANOMALY TOLERANCES
    val min_cable_radius: Double = 15.0
    val mini_delta_tolerance: Double = 0.22
    val cnn_defect_tolerance: Int = 3

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // CREATE THE KAFKA INPUT SOURCE
    val kafka_input_topic: String = "surface_data.sensor_1A"
    val source_details = kafka_utils.input_source[SENSOR_SCHEMA](kafka_input_topic)
    val kafka_input_stream: DataStream[SENSOR_SCHEMA] = env
        .fromSource(source_details._1, source_details._2, source_details._3)
        .name("KAFKA")
        .setParallelism(4)

    // // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    val vector_query: String = "INSERT INTO surface_data.sensor_1A (timestamp, serial_number, thread_id, nth_msg, vector) values (?, ?, ?, ?, ?);"

    // GATHER VECTORS INTO SLIDING MATRIX WINDOW
    val sliding_matrix_stream: DataStream[topo_utils.SCALA_MATRIX] = kafka_input_stream
        .flatMap(new topo_utils.sliding_matrix_factory(
            matrix_height,
            adjusted_matrix_height,
            vector_query
        ))
        .name("SLIDING MATRIX")
        .setParallelism(4)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // ANALYZE LARGE TENSOR FOR ANOMALIES
    val defective_tile_stream: DataStream[topo_utils.DEFECT_OUTPUT] = sliding_matrix_stream
        .flatMap(new topo_utils.tensor_processing(
            vector_length,
            matrix_height,
            tensor_depth,
            adjusted_matrix_height,
            n_mini_tiles,
            min_cable_radius,
            mini_delta_tolerance,
            cnn_defect_tolerance
        ))
        .name("TENSOR PROCESSING")
        .setParallelism(8)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // FINALLY, START THE PIPELINE
    env.execute("TOPO SURFACE PROCESSING")
}
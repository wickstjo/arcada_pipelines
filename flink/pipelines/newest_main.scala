package com.example.myproject

// SHARED
import org.apache.flink.streaming.api.scala._
import scala.collection.JavaConverters._

import utils.{kafka_utils, cassandra_utils, topo_utils}
import schemas.surface_data.{sensor_1A => SENSOR_SCHEMA, defective_tile => DEFECT_SCHEMA}

object Main extends App {

    // CREATE STREAM PROCESSING ENVIRONMENT
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

    // WHAT CABLE SECTOR PIPELINE HANDLES
    val topo_sector: String = "1A"

    // KAFKA TOPICS
    val kafka_input_topic: String = "surface_data.sensor_1A"
    val kafka_defect_topic: String = "surface_data.defects"

    // CASSANDRA QUERY STRINGS
    val defect_query: String = "INSERT INTO surface_data.defects (hash, sector) values (?, ?);"
    val vector_query: String = "INSERT INTO surface_data.sensor_1A (timestamp, serial_number) values (?, ?);"

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
    val mini_delta_tolerance: Double = 0.15
    val cnn_defect_tolerance: Int = 3

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // CREATE THE KAFKA INPUT SOURCE
    val source_details = kafka_utils.input_source[SENSOR_SCHEMA](kafka_input_topic)
    val kafka_input_stream: DataStream[SENSOR_SCHEMA] = env.fromSource(source_details._1, source_details._2, source_details._3)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // CONVERT STRUCTS TO TUPLES FOR INJECTION
    val vector_ingestion_formatting: DataStream[Tuple2[String, String]] = kafka_input_stream
        .map(item => Tuple2(
            item.getTimestamp().toString(),
            item.getSerialNumber().toString()
        ))
        .name("CASSANDRA VECTOR INGESTION")
        .setParallelism(2)
    
    // // CREATE FINAL OUTPUT SINK & ATTACH TUPLE STREAM TO IT
    val vector_sink = cassandra_utils.output_sink[Tuple2[String, String]](vector_query, vector_ingestion_formatting)
        .setParallelism(4)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // EXTRACT TOPO VECTOR FROM LARGER SCHEMA OBJECT
    val vector_extraction_stream: DataStream[topo_utils.TOPO_VECTOR] = kafka_input_stream
        .map(item => item.getDatapoints().asScala.map(_.toDouble).toArray)
        .name("TOPO VECTOR EXTRACTION")
        .setParallelism(1)

    // GATHER VECTORS INTO SLIDING MATRIX WINDOW
    val sliding_matrix_stream: DataStream[topo_utils.TOPO_VECTORS] = vector_extraction_stream
        .flatMap(new topo_utils.sliding_vector_window[topo_utils.TOPO_VECTOR](
            matrix_height,
            adjusted_matrix_height
        ))
        .name("SLIDING MATRIX CREATION")
        .setParallelism(1)

    // CREATE A TENSOR FROM FULL MATRIX
    val tensor_stream: DataStream[topo_utils.TOPO_TENSOR] = sliding_matrix_stream
        .map(item => topo_utils.vectors_to_tensor(
            item,
            vector_length,
            matrix_height,
            tensor_depth,
        ))
        .name("TENSOR CREATION")
        .setParallelism(3)

    // CREATE MANY LARGE, OVERLAPPING TILES FROM TENSOR
    val tile_stream: DataStream[topo_utils.TOPO_TENSOR] = tensor_stream
        .flatMap(new topo_utils.create_large_tiles(
            vector_length,
            matrix_height,
            adjusted_matrix_height,
        ))
        .name("LARGE TILE CREATION")
        .setParallelism(4)

    // // ANALYZE LARGE TENSOR FOR ANOMALIES
    // val tile_analysis_stream: DataStream[Tuple2[topo_utils.TOPO_TENSOR, String]] = tile_stream
    //     .flatMap(new topo_utils.analyze_large_tiles(
    //         matrix_height,
    //         n_mini_tiles,
    //         min_cable_radius,
    //         mini_delta_tolerance,
    //         cnn_defect_tolerance
    //     ))
    //     .name("LARGE TILE ANALYSIS")
    //     .setParallelism(5)

    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // // PARSE LARGE TILE INTO KAFKA DEFECT SCHEMA
    // val kafka_defect_formatting = tile_analysis_stream
    //     .map(item => {

    //         // TRANSFORM SCALA LIST TO JAVA LIST ON EACH TENSOR DIMENSION
    //         val java_tensor: topo_utils.JAVA_TENSOR = item._1.map {
    //             inner => inner.map(_.toList.map(_.asInstanceOf[java.lang.Double]).asJava).toList.asJava
    //         }.toList.asJava

    //         // CAST TILE PROPERTIES TO DEFECT SCHEMA
    //         new DEFECT_SCHEMA(item._2, topo_sector, java_tensor)
    //     })
    //     .name("KAFKA DEFECT INGESTION")
    //     .setParallelism(2)

    // // PUSH DEFECT TO KAFKA -- WILL BE CAUGHT BY CNN
    // val kafka_defect_sink = kafka_utils.output_sink[DEFECT_SCHEMA](kafka_defect_topic)
    // kafka_defect_formatting.sinkTo(kafka_defect_sink)

    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // // CONVERT STRUCTS TO TUPLES FOR INJECTION
    // val cassandra_defect_formatting: DataStream[Tuple2[String, String]] = tile_analysis_stream
    //     .map(item => Tuple2(
    //         item._1.toString(),
    //         topo_sector.toString(),
    //     ))
    //     .name("CASSANDRA DEFECT INGESTION")
    //     .setParallelism(3)
    
    // // // CREATE FINAL OUTPUT SINK & ATTACH TUPLE STREAM TO IT
    // val cassandra_defect_sink = cassandra_utils.output_sink[Tuple2[String, String]](defect_query, cassandra_defect_formatting)
    //     .setParallelism(4)

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // val output = large_tile_creation
    //     .print()
    //     .setParallelism(1)

    // FINALLY, START THE PIPELINE
    env.execute("1A TOPO PROCESSING PIPELINE")
}
package test_pipeline.streaming

// import org.apache.flink.streaming.api.scala.{StreamExecutionEnvironment, DataStream}
import org.apache.flink.streaming.api.scala._

import utils.schema_utils.{STOCK_SCHEMA, STOCK_DESERIALIZER}
import utils.kafka_utils
import utils.cassandra_utils
import utils.processing_utils

object Main extends App {

    // INITIALIZE THE STREAM PROCESSING ENVIRONMENT
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

    // ASSEMBLE THE KAFKA INPUT SOURCE
    val kafka_input_topic: String = "test_topic"
    val (kafka_src, watermark_strat, src_name) = kafka_utils.input_source[STOCK_SCHEMA, STOCK_DESERIALIZER](kafka_input_topic)

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // CREATE THE KAFKA INPUT STREAM
    val kafka_stream: DataStream[STOCK_SCHEMA] = env
        .fromSource(kafka_src, watermark_strat, src_name)
        .setParallelism(1)

    // PRINT EVERY EVENT FOR CLARITY
    kafka_stream.print()

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // PUSH EVERY ROW DIRECTLY INTO CASSANDRA
    val vector_query: String = "INSERT INTO foobar.test_table (timestamp, open, close, high, low, volume) values (?, ?, ?, ?, ?, ?);"
    cassandra_utils.output_sink[STOCK_SCHEMA](vector_query, kafka_stream)

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // GATHER VECTORS INTO SLIDING MATRIX WINDOW
    val matrix_stream: DataStream[Array[STOCK_SCHEMA]] = kafka_stream
        .flatMap(new processing_utils.sliding_matrix[STOCK_SCHEMA](2, 1))
        .name("SLIDING MATRIX")
        .setParallelism(2)

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // FINALLY, START THE PIPELINE
    env.execute("TESTING PIPELINE")
}
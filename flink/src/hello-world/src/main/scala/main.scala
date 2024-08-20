package com.example.myproject

// import org.apache.flink.streaming.api.scala.{StreamExecutionEnvironment, DataStream}
import org.apache.flink.streaming.api.scala._

import utils.schema_utils.{STOCK_SCHEMA, STOCK_DESERIALIZER}
import utils.kafka_utils
import utils.cassandra_utils

object Main extends App {

    // INITIALIZE THE STREAM PROCESSING ENVIRONMENT
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

    // CREATE THE KAFKA INPUT SOURCE
    val kafka_input_topic: String = "test_topic"
    val (kafka_src, watermark_strat, src_name) = kafka_utils.input_source[STOCK_SCHEMA, STOCK_DESERIALIZER](kafka_input_topic)

    // CREATE THE KAFKA INPUT STREAM
    val kafka_stream: DataStream[STOCK_SCHEMA] = env.fromSource(kafka_src, watermark_strat, src_name)
    kafka_stream.print()

    // PUSH STREAM ROWS DIRECTLY INTO KAFKA
    val vector_query: String = "INSERT INTO foobar.testing_table (timestamp, open, close, high, low, volume) values (?, ?, ?, ?, ?, ?);"
    cassandra_utils.output_sink[STOCK_SCHEMA](vector_query, kafka_stream)

    // FINALLY, START THE PIPELINE
    env.execute("FOOBAR")
}
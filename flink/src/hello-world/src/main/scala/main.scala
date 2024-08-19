package com.example.myproject

// import org.apache.flink.streaming.api.scala.{StreamExecutionEnvironment, DataStream}
import org.apache.flink.streaming.api.scala._

import utils.schema_utils.{STOCK_SCHEMA, STOCK_DESERIALIZER}
import utils.kafka_utils

object Main extends App {

    // INITIALIZE THE STREAM PROCESSING ENVIRONMENT
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

    // CREATE THE KAFKA INPUT SOURCE
    val kafka_input_topic: String = "eyylmaoZ"
    val (kafka_src, watermark_strat, src_name) = kafka_utils.input_source[STOCK_SCHEMA, STOCK_DESERIALIZER](kafka_input_topic)

    // CREATE THE KAFKA INPUT STREAM
    val kafka_stream: DataStream[STOCK_SCHEMA] = env.fromSource(kafka_src, watermark_strat, src_name)

    kafka_stream.print()

    // FINALLY, START THE PIPELINE
    env.execute("FOOBAR")
}
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

    val pre_processing = kafka_stream.map(item => {
        // FILTER & FORMAT THE RAW DATA STREAM
    })

    pre_processing.map(item => {
        // INJECT ALL 'CLEAN' DATA TO THE DB
    })

    val model_usage = pre_processing.map(item => {
        // USE THE MODEL
        // PUSH PREDICTION & STATISTICS FORWARD
    }).setParallelism(10)

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    model_usage.map(item => {
        // WRITE PREDICTIONS TO THE DB
    })

    model_usage.map(item => {
        // PUBLISH MODEL OUTPUT ON PROMETHEUS
    })

    val post_processing = model_usage.map(item => {
        // CHECK FOR CONDITIONAL MODEL DRIFTS
        // ONLY OUTPUT SOMETHING IF THRESHOLD IS BREACHED
    })

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    post_processing.map(item => {
        // TRAIN & DEPLOY A NEW MODEL
    })

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // FINALLY, START THE PIPELINE
    env.execute("TESTING PIPELINE")
}
package utils

import org.apache.flink.streaming.api.scala._
import scala.collection.JavaConverters._
import org.apache.flink.api.common.functions.RichFlatMapFunction
import org.apache.flink.configuration.Configuration
import org.apache.flink.util.Collector
import org.apache.flink.api.common.functions.RuntimeContext
import scala.reflect.ClassTag

object processing_utils {

    // HIDES/SHOWS PRINT STATEMENTS
    val DEBUGGING: Boolean = true

    // TYPE SHORTHANDS
    type SCALA_VECTOR = Array[Double]
    type SCALA_MATRIX = Array[SCALA_VECTOR]
    type SCALA_TENSOR = Array[SCALA_MATRIX]

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // AGGREGATE VECTORS INTO A RECURSIVELY OVERLAPPING MATRIX
    class sliding_matrix [SCHEMA: ClassTag] (
        val window_size: Int, 
        val matrix_overlap: Int
    ) extends RichFlatMapFunction[SCHEMA, Array[SCHEMA]] {

        // VECTOR ACCUMULATOR
        private var container: Array[SCHEMA] = _

        // CONSTRUCTOR
        override def open(parameters: Configuration): Unit = {

            // INITIALIZE THE CONTAINER
            container = Array()

            // FOR CLARITY, PRINT WHICH REPLICA THIS IS RUNNING ON
            if (DEBUGGING) {
                val nth_replica = getRuntimeContext.getIndexOfThisSubtask
                println(s"NTH 'sliding_matrix' STARTED (${nth_replica})")
            }
        }

        // PROCESS INCOMING VECTORS
        override def flatMap(item: SCHEMA, out: Collector[Array[SCHEMA]]): Unit = {

            // APPEND INPUT VALUE TO CONTAINER
            container = container :+ item

            // WHEN A FULL MATRIX HAS BEEN AGGREGATED
            if (container.length == window_size) {
                if (DEBUGGING) println("A FULL MATRIX AS BEEN AGGREGATED")

                // SNAPSHOT THE CURRENT MATRIX, THEN SLICE THE PREDECESSOR
                val full_matrix: Array[SCHEMA] = container.clone()
                container = container.slice(matrix_overlap, window_size)

                // FINALLY, PUSH THE FULL MATRIX TO THE NEXT PIPELINE STAGE
                out.collect(full_matrix)
            }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
}

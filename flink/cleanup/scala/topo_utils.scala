package utils

import org.apache.flink.streaming.api.scala._
import org.apache.flink.api.common.functions.RichFlatMapFunction
import org.apache.flink.configuration.Configuration
import org.apache.flink.util.Collector

import org.apache.flink.api.common.functions.FlatMapFunction

import java.nio.ByteBuffer
import java.security.MessageDigest

////////////////

import schemas.surface_data.{sensor_1A => SENSOR_SCHEMA, defective_tile => DEFECT_SCHEMA}
import scala.collection.JavaConverters._

import com.datastax.oss.driver.api.core.{CqlSession}
import com.datastax.oss.driver.api.core.cql.{BoundStatement, PreparedStatement, BatchStatement, BatchType, AsyncResultSet}
import java.net.{InetSocketAddress}
import java.util.{ArrayList, Collection}
import java.util.function.BiConsumer

import org.apache.flink.api.common.functions.RuntimeContext

object topo_utils {

    // HIDES/SHOWS PRINT STATEMENTS
    val DEBUGGING: Boolean = false

    // TYPE SHORTHANDS
    type SCALA_VECTOR = Array[Double]
    type SCALA_MATRIX = Array[SCALA_VECTOR]
    type SCALA_TENSOR = Array[SCALA_MATRIX]

    type JAVA_VECTOR = java.util.List[java.lang.Double]
    type JAVA_MATRIX = java.util.List[JAVA_VECTOR]
    type JAVA_TENSOR = java.util.List[JAVA_MATRIX]

    type DEFECT_OUTPUT = Tuple5[SCALA_TENSOR, Tuple4[Double, Double, Double, Double], String, String, Int]

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // SLIDING WINDOW STREAM COLLECTOR
    class sliding_matrix_factory (
        val window_size: Int, 
        val slide_by: Int,
        val cassandra_query: String
    ) extends RichFlatMapFunction[SENSOR_SCHEMA, SCALA_MATRIX] {

        // VECTOR ACCUMULATOR
        private var container: SCALA_MATRIX = _

        // CASSANDRA SESSION
        private var session: CqlSession = _
        private var prepared_statement: PreparedStatement = _
        private var batch_statement: BatchStatement = _
        
        // DB BATCH WRITING
        private var write_batch: List[BoundStatement] = _
        private var batch_capacity: Int = _

        private var nth_msg: Int = _
        private var nth_replica: Int = _

        // CREATE A CASSANDRA SESSION
        def cassandra_session(): Unit = {

            // CREATE THE CASSANDRA CONNECTION STRING
            val cassandra_machines: List[Int] = List(204, 218, 163, 149)
            val cassandra_endpoints: Collection[InetSocketAddress] = new ArrayList[InetSocketAddress]()

            cassandra_machines.foreach(
                ip_suffix => cassandra_endpoints.add(
                    new InetSocketAddress("192.168.1." + ip_suffix, 9042)
                )
            )

            // CREATE CASSANDRA SESSION
            session = CqlSession.builder()
                .addContactPoints(cassandra_endpoints)
                .withLocalDatacenter("DATACENTER1")
                .build()

            // CREATE REUSABLE PREPARED STATEMENT
            prepared_statement = session.prepare(cassandra_query)
            write_batch = List()
            batch_capacity = 4
        }

        // CONSTRUCTOR
        override def open(parameters: Configuration): Unit = {
            container = Array()
            cassandra_session()

            nth_replica = getRuntimeContext.getIndexOfThisSubtask
            nth_msg = 0
        }

        // STREAM OPERATION
        override def flatMap(item: SENSOR_SCHEMA, out: Collector[SCALA_MATRIX]): Unit = {

            // APPEND INPUT VALUE TO CONTAINER
            val to_scala: SCALA_VECTOR = item.getDatapoints().asScala.map(_.toDouble).toArray
            container = container :+ to_scala

            // WHEN ENOUGH VALUES HAVE BEEN GATHERED
            if (container.length == window_size) {

                // CLONE THE FULL MATRIX, THEN ROLL BACK THE ORIGINAL
                val cloned: SCALA_MATRIX = container.clone()
                container = container.slice(slide_by, window_size)

                // PUSH THE CLONE FORWARD
                out.collect(cloned)
            }

            // val result = session.executeAsync(
            val result = session.executeAsync(
                prepared_statement.bind(
                    item.getTimestamp().toString(),
                    item.getSerialNumber().toString(),
                    nth_replica.toString(),
                    nth_msg.toString(),
                    item.getDatapoints()
                )
            )

            nth_msg += 1

            // // Attach a CompletionStage listener to the resultSetFuture
            // result.whenComplete(new BiConsumer[AsyncResultSet, Throwable] {
            //     override def accept(resultSet: AsyncResultSet, throwable: Throwable): Unit = {
            //         if (throwable != null) {
            //             // Handle the exception
            //             throwable.printStackTrace()
            //         }
            //     }
            // })


            // // ADD ROW TO NEXT DB BATCH
            // write_batch = write_batch :+ prepared_statement.bind(
            //     item.getTimestamp().toString(),
            //     item.getSerialNumber().toString(),
            //     item.getDatapoints()
            // )

            // // WHEN CAPACITY IS MET, WRITE BATCH TO DB
            // if (write_batch.length >= batch_capacity) {

            //     // INSTANTIATE NEW BATCH STATEMENT
            //     var batch_statement = BatchStatement.builder(BatchType.LOGGED)

            //     // COPY THE BATCH TO ANOTHER ARRAY, THEN RESET THE ORIGINAL
            //     val deep_copy = write_batch.toList
            //     write_batch = List()

            //     // ADD EACH BOUND STATEMENT TO THE BATCH
            //     deep_copy.foreach(
            //         item => batch_statement.addStatement(item)
            //     )

            //     // WRITE TO DB & RESET THE BATCH COLLECTION
            //     val completed_batch = batch_statement.build()
            //     val result = session.executeAsync(completed_batch)
            //     // val result = session.execute(completed_batch)

            //     // result.whenComplete { (resultSet: ResultSet, throwable: Throwable) =>
            //     //     if (throwable != null) {
            //     //         throwable.printStackTrace()
            //     //     }
            //     // }
            // }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // BREAK TENSOR INTO MANY LARGE, OVERLAPPING TILES
    class tensor_processing (
        val vector_length: Int,
        val matrix_height: Int,
        val tensor_depth: Int,
        val adjusted_matrix_height: Int,
        val n_mini_tiles: Int,
        val min_cable_radius: Double,
        val mini_delta_tolerance: Double,
        val cnn_defect_tolerance: Int,
    ) extends RichFlatMapFunction[SCALA_MATRIX, DEFECT_OUTPUT] {
        override def flatMap(input_matrix: SCALA_MATRIX, out: Collector[DEFECT_OUTPUT]): Unit = {

            // CREATE TENSOR CONTAINER
            val tensor: SCALA_TENSOR = Array.ofDim[Double](
                vector_length, 
                matrix_height, 
                tensor_depth
            )
            
            // FILL THE TENSOR WITH VECTOR VALUES
            for (x <- 0 until vector_length; y <- 0 until matrix_height; z <- 0 until tensor_depth) {
                tensor(x)(y)(z) = input_matrix(y)(x)
            }

        ////////////////////////////
        ////////////////////////////

            // STATIC X POSITIONS
            val large_x0: Int = 0
            val large_x1: Int = matrix_height
        
            // DYNAMICALLY SELECT Y POSITIONS
            for (nth_large <- Range(0, vector_length, adjusted_matrix_height)) {

                // CURRENT Y POSITIONS
                var large_y0: Int = nth_large
                var large_y1: Int = nth_large + matrix_height

                // FIX POTENTIAL SIZE OVERFLOW
                if (large_y1 > vector_length) {
                    large_y0 = vector_length - matrix_height
                    large_y1 = vector_length   
                }

                // SELECT THE NEXT LARGE SUB-TILE
                val large_tile: SCALA_TENSOR = select_tile(tensor, Tuple4(
                    large_x0, large_x1, large_y0, large_y1
                ))

            ////////////////////////////
            ////////////////////////////

                // COMPUTE DESIRED MINI TILE WIDTH
                val mini_tile_width: Int = math.ceil(matrix_height.toDouble / n_mini_tiles.toDouble).toInt
                
                // COMPUTE SOME STATISTICS ON LARGE TILE
                var large_tile_stats = tile_stats(large_tile)
                var (large_mx, large_mn, large_delta, large_mean) = large_tile_stats
                
                // INTERRUPT ITERATION WHEN ALL NANs ARE FOUND
                if (large_mean.isNaN) {
                    if (DEBUGGING) println("SKIPPING: LARGE TILE IS NAN")

                // INTERRUPT LOOP IF CABLE RADIUS IS TOO SMALL
                } else if (large_mean < min_cable_radius) {
                    if (DEBUGGING) println("SKIPPING: BAD CABLE RADIUS (" + large_mean + " < " + min_cable_radius + ")")

                // OTHERWISE, PROCEED FURTHER
                } else {

                    // IF THE IMAGE IS TOO FLAT, ENLARGE IT
                    if (large_delta < 0.3) {

                        // KEEP ORIGINAL VALUES INTACT
                        val mx2 = large_mx
                        val mn2 = large_mn

                        // COMPUTE NEW ONES
                        large_mx = ((mx2 + mn2) / 2.0) + 0.15
                        large_mn = ((mx2 + mn2) / 2.0) - 0.15
                    }

                    // TRACK DEFECTIVE TILE COUNT
                    var defects_found: Int = 0
                    var report_sent: Boolean = false

                    // START LOOPING THROUGH SQUARE MINI-TILES
                    for (x <- 0 until n_mini_tiles; y <- 0 until n_mini_tiles) {

                        // STOP SEARCHING WHEN ENOUGH DEFECTIVE TILES HAVE BEEN FOUND
                        if (report_sent == false) {

                            // COMPUTE THE MINI-TILE POSITION
                            val small_x0: Int = math.min(x * mini_tile_width, matrix_height)
                            val small_x1: Int = math.min(small_x0 + mini_tile_width, matrix_height)
                            val small_y0: Int = math.min(y * mini_tile_width, matrix_height)
                            val small_y1: Int = math.min(small_y0 + mini_tile_width, matrix_height)

                            // SELECT THE MINI TILE-- XY POSITIONS FLIPPED FOR WHATEVER REASON
                            val mini_tile: SCALA_TENSOR = select_tile(large_tile, Tuple4(
                                small_x0, small_x1, small_y0, small_y1
                            ))

                            // COMPUTE SOME STATISTICS ON SMALL TILE
                            var (mini_mx, mini_mn, mini_delta, mini_mean) = tile_stats(mini_tile)
                            
                            // SKIP FULL NAN TILES
                            if (mini_mean.isNaN) {
                                if (DEBUGGING) println("SKIPPING: MINI TILE IS NAN")
                            
                            // DEFECTIVE MINI TILE FOUND
                            } else if (mini_delta > mini_delta_tolerance) {
                                defects_found += 1

                                if (DEBUGGING) println("MINI DEFECT FOUND")
                            }

                            // IF ENOUGH MINI TILES WERE FOUND
                            if (defects_found >= cnn_defect_tolerance) {

                                if (DEBUGGING) println("LARGE TILE SENT FOR CNN ANALYSIS")

                                // HASH THE LARGE TENSOR FOR REFERENCE
                                val large_hash = hash_tensor(large_tile)

                                // GET CURRENT TIMESTAMP
                                val timestamp: String = System.currentTimeMillis.toString

                                // PUSH LARGE TILE FOR FURTHER ANALYSIS
                                out.collect(Tuple5(
                                    large_tile, large_tile_stats, large_hash, timestamp, defects_found
                                ))

                                // TOGGLE REPORT STATUS TO SKIP REMAINING MINI TILES
                                report_sent = true
                            }
                        }
                    }
                }
            }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // SLIDING WINDOW STREAM COLLECTOR
    class defect_ingestion_factory (
        val cassandra_query: String
    ) extends RichFlatMapFunction[DEFECT_OUTPUT, Boolean] {

        // CASSANDRA SESSION
        private var session: CqlSession = _
        private var prepared_statement: PreparedStatement = _

        // CREATE A CASSANDRA SESSION
        def cassandra_session(): Unit = {

            // CREATE THE CASSANDRA CONNECTION STRING
            val cassandra_machines: List[Int] = List(204, 218, 163)
            val cassandra_endpoints: Collection[InetSocketAddress] = new ArrayList[InetSocketAddress]()

            cassandra_machines.foreach(
                ip_suffix => cassandra_endpoints.add(
                    new InetSocketAddress("192.168.1." + ip_suffix, 9042)
                )
            )

            // CREATE CASSANDRA SESSION
            session = CqlSession.builder()
                .addContactPoints(cassandra_endpoints)
                .withLocalDatacenter("DATACENTER1")
                .build()

            // CREATE REUSABLE PREPARED STATEMENT
            prepared_statement = session.prepare(cassandra_query)
        }

        // CONSTRUCTOR
        override def open(parameters: Configuration): Unit = {
            cassandra_session()
        }

        // STREAM OPERATION
        override def flatMap(item: DEFECT_OUTPUT, out: Collector[Boolean]): Unit = {

            // EXTRACT TILE STATS FOR CLARITY
            var (large_mx, large_mn, large_delta, large_mean) = item._2

            // WHAT CABLE SECTOR PIPELINE HANDLES
            val topo_sector: String = "1A"

            // INGEST PAYLOAD INTO THE DB
            session.executeAsync(
                prepared_statement.bind(
                    item._4.toString(),
                    item._3.toString(),
                    topo_sector.toString(),
                    large_mx.asInstanceOf[java.lang.Double], 
                    large_mn.asInstanceOf[java.lang.Double], 
                    large_delta.asInstanceOf[java.lang.Double], 
                    large_mean.asInstanceOf[java.lang.Double], 
                    item._5.asInstanceOf[java.lang.Integer],
                )
            )

            out.collect(true)
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // HASH TENSOR VALUES WITH SHA256 -- FOR VALIDATION
    def hash_tensor(container: SCALA_TENSOR): String = {
        
        // CREATE HASH INSTANCE & DIGEST BYTE ARRAY
        val sha256 = MessageDigest.getInstance("SHA-256")
        
        // LOOP THROUGH EACH VECTOR
        for (matrix <- container) {
            for (vector <- matrix) {
                
                // CONVERT VECTOR TO BYTES
                val byteBuffer = ByteBuffer.allocate(vector.length * 8)
                vector.foreach(byteBuffer.putDouble(_))
                byteBuffer.flip()
                val byteString = byteBuffer.array()
                
                // DIGEST BYTE VECTOR
                sha256.update(byteString)
            }
        }
        
        // RETURN HASH AS STRING
        val hashBytes = sha256.digest()
        return hashBytes.map("%02x".format(_)).mkString
    }

    // SELECT A TILE FROM A TENSOR
    def select_tile(larger_tensor: SCALA_TENSOR, positions: Tuple4[Int, Int, Int, Int]): SCALA_TENSOR = {

        // DESTRUCTURE POSITIONAL INDECIES
        val (x0, x1, y0, y1) = positions

        // SLICE AND RETURN SMALLER SUBSET
        return larger_tensor.slice(y0, y1).map(_.slice(x0, x1))
    }

    // COMPUTE SOME BASIC STATISTICS OF A TENSOR TILE
    def tile_stats(input_data: SCALA_TENSOR): Tuple4[Double, Double, Double, Double] = {
        
        // FLATTEN THE 3D ARRAY & NUKE NANs
        val flat_nonan = input_data.flatten.flatten.filter(!_.isNaN)
        
        // BREAK EARLY FOR ALL NANs
        if (flat_nonan.length == 0) {
            return Tuple4(Double.NaN, Double.NaN, Double.NaN, Double.NaN)
        }
        
        // COMPUTE MINMAX VALUES
        val mx: Double = flat_nonan.maxBy(identity)
        val mn: Double  = flat_nonan.minBy(identity)
        val delta: Double = mx - mn
        
        // COMPUTE MEAN VALUE
        val sum = flat_nonan.sum
        val mean = sum / input_data.length
        
        // RETURN ALL OF THEM
        return Tuple4(mx, mn, delta, mean)
    }
}

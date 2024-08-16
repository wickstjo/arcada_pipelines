package utils

import org.apache.flink.streaming.api.scala._
import org.apache.flink.api.common.functions.RichFlatMapFunction
import org.apache.flink.configuration.Configuration
import org.apache.flink.util.Collector
import scala.reflect.ClassTag

import org.apache.flink.api.common.functions.FlatMapFunction

import java.nio.ByteBuffer
import java.security.MessageDigest

object topo_utils {

    // HIDES/SHOWS PRINT STATEMENTS
    val DEBUGGING: Boolean = true

    // TYPE SHORTHANDS
    type TOPO_VECTOR = Array[Double]
    type TOPO_VECTORS = Array[TOPO_VECTOR]
    type TOPO_TENSOR = Array[TOPO_VECTORS]
    type JAVA_TENSOR = java.util.List[java.util.List[java.util.List[java.lang.Double]]]

    // SLIDING WINDOW STREAM COLLECTOR
    class sliding_vector_window[T: ClassTag] (
        val window_size: Int, 
        val slide_by: Int
    ) extends RichFlatMapFunction[T, Array[T]] {

        // SERVERSE SPOT FOR ACCUMULATOR DS
        private var container: Array[T] = _

        // CONSTRUCTOR
        override def open(parameters: Configuration): Unit = {
            container = Array()
        }

        // INGEST NEW DATA INTO WINDOW
        def ingest(input: T): Array[T] = {

            // APPEND INPUT VALUE TO CONTAINER
            container = container :+ input

            // WHEN ENOUGH VALUES HAVE BEEN GATHERED
            if (container.length == window_size) {
                return extract_and_shift()
            }
            
            // OTHERWISE, RETURN NULL
            return null
        }
        
        // EXTRACT & SHIFT WINDOW
        def extract_and_shift(): Array[T] = {
            
            // CLONE CONTAINER & SHIFT THE OLD ONE FORWARD
            val cloned: Array[T] = container.clone()
            container = container.slice(slide_by, window_size)

            // THEN, RETURN THE CLONE
            return cloned
        }

        // STREAM OPERATION
        override def flatMap(value: T, out: Collector[Array[T]]): Unit = {

            // INGEST VECTOR INTO COLLECTION
            val result = ingest(value)

            // WHEN A FULL WINDOW HAS BEEN COLLECTED, PUSH IT FORWARD
            if (result != null) {
                out.collect(result)
            }
        }
    }

    // CONVERT LIST OF VECTORS TO TENSOR
    def vectors_to_tensor(
        input_vectors: TOPO_VECTORS,
        vector_length: Int,
        matrix_height: Int,
        tensor_depth: Int
    ): TOPO_TENSOR = {
        
        // CREATE TENSOR CONTAINER
        var tensor: TOPO_TENSOR = Array.ofDim[Double](
            vector_length, 
            matrix_height, 
            tensor_depth
        )
        
        // FILL THE TENSOR WITH VECTOR VALUES
        for (x <- 0 until vector_length; y <- 0 until matrix_height; z <- 0 until tensor_depth) {
            tensor(x)(y)(z) = input_vectors(y)(x)
        }

        // PRINT TENSOR HASH FOR VALIDATION WHEN DEBUGGING
        if (DEBUGGING) {
            val my_hash: String = topo_utils.hash_tensor(tensor)
            println(my_hash)
        }
        
        return tensor
    }

    // BREAK TENSOR INTO MANY LARGE, OVERLAPPING TILES
    class create_large_tiles (
        val vector_length: Int,
        val matrix_height: Int,
        val adjusted_matrix_height: Int
    ) extends RichFlatMapFunction[TOPO_TENSOR, TOPO_TENSOR] {
        override def flatMap(full_tensor: TOPO_TENSOR, out: Collector[TOPO_TENSOR]): Unit = {

            // STATIC X POSITIONS
            val x0: Int = 0
            val x1: Int = matrix_height
        
            // DYNAMICALLY SELECT Y POSITIONS
            for (nth_large <- Range(0, vector_length, adjusted_matrix_height)) {

                // CURRENT Y POSITIONS
                var y0: Int = nth_large
                var y1: Int = nth_large + matrix_height

                // FIX POTENTIAL SIZE OVERFLOW
                if (y1 > vector_length) {
                    y0 = vector_length - matrix_height
                    y1 = vector_length   
                }

                // SELECT THE NEXT LARGE SUB-TILE
                val large_tile: TOPO_TENSOR = select_tile(full_tensor, Tuple4(
                    x0, x1, y0, y1
                ))

                // PRINT TILE HASH FOR VALIDATION WHEN DEBUGGING
                if (DEBUGGING) {
                    val large_hash = hash_tensor(large_tile)
                    println("\t", large_hash)
                }

                // PUSH LARGE TILE TO NEXT PIPELINE STAGE
                out.collect(large_tile)
            }
        }
    }

    // ANALYZE LARGE TILES FOR DEFECTS
    class analyze_large_tiles (
        val matrix_height: Int,
        val n_mini_tiles: Int,
        val min_cable_radius: Double,
        val mini_delta_tolerance: Double,
        val cnn_defect_tolerance: Int,
    ) extends RichFlatMapFunction[TOPO_TENSOR, Tuple2[topo_utils.TOPO_TENSOR, String]] {
        override def flatMap(large_tile: TOPO_TENSOR, out: Collector[Tuple2[topo_utils.TOPO_TENSOR, String]]): Unit = {

            // COMPUTE DESIRED MINI TILE WIDTH
            val mini_tile_width: Int = math.ceil(matrix_height.toDouble / n_mini_tiles.toDouble).toInt
            
            // COMPUTE SOME STATISTICS ON LARGE TILE
            var (large_mx, large_mn, large_delta, large_mean) = tile_stats(large_tile)
            
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

                // START LOOPING THROUGH SQUARE MINI-TILES
                for (x <- 0 until n_mini_tiles; y <- 0 until n_mini_tiles) {

                    // COMPUTE THE MINI-TILE POSITION
                    val x0: Int = math.min(x * mini_tile_width, matrix_height)
                    val x1: Int = math.min(x0 + mini_tile_width, matrix_height)
                    val y0: Int = math.min(y * mini_tile_width, matrix_height)
                    val y1: Int = math.min(y0 + mini_tile_width, matrix_height)

                    // SELECT THE MINI TILE-- XY POSITIONS FLIPPED FOR WHATEVER REASON
                    val mini_tile: TOPO_TENSOR = select_tile(large_tile, Tuple4(
                        y0, y1, x0, x1
                    ))

                    // PRINT TILE HASH FOR VALIDATION WHEN DEBUGGING
                    if (DEBUGGING) {
                        val mini_hash = hash_tensor(mini_tile)
                        println("\t\t", mini_hash)
                    }
                    
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

                    // WITH ENOUGH DEFECTS
                    if (defects_found >= cnn_defect_tolerance) {

                        if (DEBUGGING) println("LARGE TILE SENT FOR CNN ANALYSIS")

                        // HASH THE LARGE TENSOR FOR REFERENCE
                        val large_hash = hash_tensor(large_tile)

                        // PUSH LARGE TILE FOR FURTHER ANALYSIS
                        out.collect(Tuple2(large_tile, large_hash))
                    }
                }
            }
        }
    }

    // HASH TENSOR VALUES WITH SHA256 -- FOR VALIDATION
    def hash_tensor(container: TOPO_TENSOR): String = {
        
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
    def select_tile(source: TOPO_TENSOR, positions: Tuple4[Int, Int, Int, Int]): TOPO_TENSOR = {
        
        // EXTRACT THE TENSOR DIMENSION
        // val n_channels: Int = source(0)(0).length
        val n_channels: Int = 3

        // DESTRUCTURE POSITIONAL INDECIES
        val (x0, x1, y0, y1) = positions
        
        // FIGURE OUT ARRAY DIMENSIONS
        val x_len = x1 - x0
        val y_len = y1 - y0

        // CREATE ARRAY FOR WINDOW
        val container: TOPO_TENSOR = Array.ofDim[Double](y_len, x_len, n_channels)

        // LOOP IN VALUES
        for (y <- y0 until y1; x <- x0 until x1; z <- 0 until n_channels) {
            container(y - y0)(x - x0)(z) = source(y)(x)(z)
        }

        return container
    }

    // COMPUTE SOME BASIC STATISTICS OF A TENSOR TILE
    def tile_stats(input_data: TOPO_TENSOR): Tuple4[Double, Double, Double, Double] = {
        
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

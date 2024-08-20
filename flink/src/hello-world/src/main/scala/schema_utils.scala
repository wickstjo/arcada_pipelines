package utils

import org.apache.flink.api.common.serialization.DeserializationSchema
import org.apache.flink.api.common.typeinfo.TypeInformation
import java.io.IOException

object schema_utils {

    // THE SCHEMA
    case class STOCK_SCHEMA(
        timestamp: Int,
        open: Float,
        high: Float,
        low: Float,
        close: Float,
        volume: Int
    )

    // THE SCHEMA DESERIALIZER
    class STOCK_DESERIALIZER extends DeserializationSchema[STOCK_SCHEMA] {

        @throws[IOException]
        override def deserialize(message: Array[Byte]): STOCK_SCHEMA = {

            // ATTEMPT TO DESERIALIZE THE DATA
            try {

                // PARSE THE JSON DATA
                val json_string = new String(message, "UTF-8")
                val json_data = ujson.read(json_string)
                
                // CAST IT TO THE OBJECT
                STOCK_SCHEMA(
                    json_data("timestamp").num.toInt,
                    json_data("open").num.toFloat,
                    json_data("high").num.toFloat,
                    json_data("low").num.toFloat,
                    json_data("close").num.toFloat,
                    json_data("volume").num.toInt
                )

            // CATCH ERRORS WITHOUT CRASHING
            } catch {
                case error: Throwable => {
                    println(s"DESERIALIZATION ERROR: ${error.getMessage}")
                    null
                }
            }
        }
        
        override def isEndOfStream(nextElement: STOCK_SCHEMA): Boolean = false
        override def getProducedType: TypeInformation[STOCK_SCHEMA] = TypeInformation.of(classOf[STOCK_SCHEMA])
    }
}
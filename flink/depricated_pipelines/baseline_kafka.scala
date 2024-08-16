// import org.apache.flink.api.common.eventtime.WatermarkStrategy
// import org.apache.flink.connector.kafka.source.KafkaSource
// import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer
// import org.apache.flink.streaming.api.scala._
// import org.apache.flink.api.common.typeinfo.TypeInformation

// // import org.apache.flink.api.common.serialization.SimpleStringSchema
// import org.apache.flink.api.common.serialization.{DeserializationSchema}
// import play.api.libs.json.{Json, JsValue}

// case class MyData(var name: String, age: Int) {
//     def update_name(new_name: String): Unit = {
//         this.name = new_name
//     }
// }

// class my_deserializer extends DeserializationSchema[MyData] {
//     override def deserialize(message: Array[Byte]): MyData = {

//         // PARSE THE BYTE ARRAY INTO A JsValue OBJECT
//         val stringified = new String(message)

//         // ATTEMPT TO PARSE IT AS A JSON-LIKE OBJECT
//         try {
//             val parsed = Json.parse(stringified)

//             // val name = (parsed \ "name").as[String]
//             // val age = (parsed \ "age").as[Int]

//             return MyData(
//                 parsed("name").as[String],
//                 parsed("age").as[Int],
//             )

//         // CATCH ERRORS SILENTLY
//         } catch {
//             case _: Throwable => {
//                 println("COULD NOT PARSE RECEIVED MESSAGE");
//                 null
//             }
//         }
//     }

//     // AUXILLARY METHODS
//     override def isEndOfStream(nextElement: MyData): Boolean = false
//     override def getProducedType: TypeInformation[MyData] = TypeInformation.of(classOf[MyData])
// }

// object Main extends App {
    
//     // SET TYPEINFO & CREATE THE ENVIRONMENT CONTEXT
//     implicit val typeInfo = TypeInformation.of(classOf[(MyData)])
//     val env = StreamExecutionEnvironment.getExecutionEnvironment

//     // TOPIC DETAILS
//     val input_topic = "topic1"
//     val consumer_group = input_topic + ".flink_consumers"

//     // CREATE THE KAFKA INPUT SOURCE
//     val kafka_source = KafkaSource.builder()
//         .setBootstrapServers("kafka_broker_1:11000")
//         // .setBootstrapServers("localhost:10001")
//         .setTopics(input_topic)
//         .setGroupId(consumer_group)
//         .setStartingOffsets(OffsetsInitializer.latest())
//         .setValueOnlyDeserializer(new my_deserializer())
//         .build()

//     // RAW KAFKA INPUT STREAM
//     val data_stream = env.fromSource(kafka_source, WatermarkStrategy.noWatermarks(), "kafka input")
//         .setParallelism(3)

//     // FILTER BASED ON AGE
//     val filtered_stream = data_stream
//         .filter(item => item.age >= 4)
//         .name("filtering phase")
//         .setParallelism(6)

//     // UPDATE NAME PROPERTY
//     val updated_stream = filtered_stream
//         .map(item => item.update_name("foobar"))
//         .name("updating phase")
//         .setParallelism(4)
    
//     // DUMP DATA INTO SINK
//     val final_sink = updated_stream
//         .print()
//         .name("sink phase")
//         .setParallelism(1)

//     // FINALLY, START THE APPLICATION
//     env.execute("read from kafka source")
// }
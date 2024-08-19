
// The simplest possible sbt build file is just one line:

scalaVersion := "2.12.3"
// That is, to create a valid sbt build, all you've got to do is define the
// version of Scala you'd like your project to use.

// ============================================================================

// Lines like the above defining `scalaVersion` are called "settings". Settings
// are key/value pairs. In the case of `scalaVersion`, the key is "scalaVersion"
// and the value is "2.13.8"

// It's possible to define many kinds of settings, such as:

name := "hello-world"
organization := "ch.epfl.scala"
version := "1.0"

// Note, it's not required for you to define these three settings. These are
// mostly only necessary if you intend to publish your library's binaries on a
// place like Sonatype.


// Want to use a published library in your project?
// You can define other libraries as dependencies in your build like this:

// libraryDependencies += "org.scala-lang.modules" %% "scala-parser-combinators" % "2.1.1"

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

// https://mvnrepository.com/artifact/org.apache.flink/flink-streaming-scala
libraryDependencies += "org.apache.flink" % "flink-streaming-scala_2.12" % "1.17.1"



// https://mvnrepository.com/artifact/org.apache.flink/flink-streaming-scala
libraryDependencies += "com.typesafe.play" %% "play-json" % "2.10.0-RC6"

libraryDependencies += "com.lihaoyi" %% "ujson" % "2.0.0"

// https://mvnrepository.com/artifact/org.apache.flink/flink-clients
libraryDependencies += "org.apache.flink" % "flink-clients" % "1.17.1"

// https://mvnrepository.com/artifact/org.apache.flink/flink-connector-kafka
libraryDependencies += "org.apache.flink" % "flink-connector-kafka" % "1.17.1"

// https://mvnrepository.com/artifact/org.apache.flink/flink-connector-cassandra
// libraryDependencies += "org.apache.flink" % "flink-connector-cassandra_2.12" % "1.17.1"
libraryDependencies ++= Seq(
    "org.apache.flink" %% "flink-connector-cassandra" % "1.16.0", //3.1.0-1.17
    "com.datastax.oss" % "java-driver-core" % "4.12.0",
    "com.codahale.metrics" % "metrics-core" % "3.0.2"
)

// https://mvnrepository.com/artifact/org.apache.flink/flink-avro-confluent-registry
// libraryDependencies += "org.apache.flink" % "flink-avro-confluent-registry" % "1.17.1"
// resolvers += "confluent" at "https://packages.confluent.io/maven/"

// // https://mvnrepository.com/artifact/org.apache.flink/flink-scala
// libraryDependencies += "org.apache.flink" %% "flink-scala" % "1.16.1"

// // https://mvnrepository.com/artifact/org.apache.flink/flink-avro
// libraryDependencies += "org.apache.flink" % "flink-avro" % "1.17.1"

// // JSON CONVERTER
// libraryDependencies += "com.typesafe.play" %% "play-json" % "2.9.2"

// FOR COMPILING AVRO SCHEMAS
// libraryDependencies += "org.apache.avro" % "avro-tools" % "1.10.2" % "provided"

// libraryDependencies += "io.confluent" % "kafka-avro-serializer" % "5.5.2"

// libraryDependencies += "io.confluent" % "kafka-streams-avro-serde" % "5.5.2"

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

assemblyMergeStrategy in assembly := {
    case PathList("META-INF", xs @ _*) => MergeStrategy.discard
    case x => MergeStrategy.first
}

// assemblyMergeStrategy in assembly := {
//     case PathList("META-INF", xs @ _*) => MergeStrategy.discard
//     case x => MergeStrategy.defaultMergeStrategy(x)
// }

// Here, `libraryDependencies` is a set of dependencies, and by using `+=`,
// we're adding the scala-parser-combinators dependency to the set of dependencies
// that sbt will go and fetch when it starts up.
// Now, in any Scala file, you can import classes, objects, etc., from
// scala-parser-combinators with a regular import.

// TIP: To find the "dependency" that you need to add to the
// `libraryDependencies` set, which in the above example looks like this:

// "org.scala-lang.modules" %% "scala-parser-combinators" % "2.1.1"

// You can use Scaladex, an index of all known published Scala libraries. There,
// after you find the library you want, you can just copy/paste the dependency
// information that you need into your build file. For example, on the
// scala/scala-parser-combinators Scaladex page,
// https://index.scala-lang.org/scala/scala-parser-combinators, you can copy/paste
// the sbt dependency from the sbt box on the right-hand side of the screen.

// IMPORTANT NOTE: while build files look _kind of_ like regular Scala, it's
// important to note that syntax in *.sbt files doesn't always behave like
// regular Scala. For example, notice in this build file that it's not required
// to put our settings into an enclosing object or class. Always remember that
// sbt is a bit different, semantically, than vanilla Scala.

// ============================================================================

// Most moderately interesting Scala projects don't make use of the very simple
// build file style (called "bare style") used in this build.sbt file. Most
// intermediate Scala projects make use of so-called "multi-project" builds. A
// multi-project build makes it possible to have different folders which sbt can
// be configured differently for. That is, you may wish to have different
// dependencies or different testing frameworks defined for different parts of
// your codebase. Multi-project builds make this possible.

// Here's a quick glimpse of what a multi-project build looks like for this
// build, with only one "subproject" defined, called `root`:

// lazy val root = (project in file(".")).
//   settings(
//     inThisBuild(List(
//       organization := "ch.epfl.scala",
//       scalaVersion := "2.13.8"
//     )),
//     name := "hello-world"
//   )

// To learn more about multi-project builds, head over to the official sbt
// documentation at http://www.scala-sbt.org/documentation.html

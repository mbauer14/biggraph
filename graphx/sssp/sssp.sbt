name := "SSSP"

version := "1.0"

scalaVersion := "2.10.4"

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.5.0"
libraryDependencies += "org.apache.spark" %% "spark-graphx" % "1.5.0"
libraryDependencies += "org.apache.hadoop" % "hadoop-client" % "2.6.0"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"

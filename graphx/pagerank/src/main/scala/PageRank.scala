/*** SimpleApp.scala ***/
import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import scala.collection.mutable.ArrayBuffer


object PageRank {

    def main(args: Array[String]) {
        val appName = "CS-838-Final-PageRank"
        val master = "spark://10.0.1.56:7077"

        // Open correct file from HDFS, supplied as first arg
        val inputLocation = args(0)

        val conf = new SparkConf()
        conf.set("spark.driver.memory", "1g")
        conf.set("spark.eventLog.enabled", "true")
        conf.set("spark.eventLog.dir", "/home/ubuntu/storage/logs")
        conf.set("spark.executor.memory", "21000m")
        conf.set("spark.executor.cores", "4")
        conf.set("spark.task.cpus", "1")
        val sc = new SparkContext(conf)

        // Load the edges as a graph
        val graph = GraphLoader.edgeListFile(sc, inputLocation)
        // Run PageRank
        val ranks = graph.pageRank(0.0001).vertices
        // Join the ranks with the usernames
        val users = sc.textFile("/graphx/data/users.txt").map { line =>
              val fields = line.split(",")
                (fields(0).toLong, fields(1))
        }
        val ranksByUsername = users.join(ranks).map {
              case (id, (username, rank)) => (username, rank)
        }
        // Print the result
        println(ranksByUsername.collect().mkString("\n"))

    }
}

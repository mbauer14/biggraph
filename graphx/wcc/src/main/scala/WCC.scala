/*** SimpleApp.scala ***/
import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import scala.collection.mutable.ArrayBuffer


object WCC {
    def main(args: Array[String]) {
        val appName = "CS-838-Assignment3-PartC"
        val master = "spark://10.0.1.56:7077"

        val conf = new SparkConf()
        conf.set("spark.driver.memory", "1g")
        conf.set("spark.eventLog.enabled", "true")
        conf.set("spark.eventLog.dir", "/home/ubuntu/storage/logs")
        conf.set("spark.executor.memory", "21000m")
        conf.set("spark.executor.cores", "4")
        conf.set("spark.task.cpus", "1")
        val sc = new SparkContext(conf)

        // Load the graph as in the PageRank example
        val graph = GraphLoader.edgeListFile(sc, "/graphx/data/followers.txt")
        // Find the connected components
        val cc = graph.connectedComponents().vertices
        // Join the connected components with the usernames
        val users = sc.textFile("/graphx/data/users.txt").map { line =>
              val fields = line.split(",")
                (fields(0).toLong, fields(1))
        }
        val ccByUsername = users.join(cc).map {
              case (id, (username, cc)) => (username, cc)
        }
        // Print the result
        println(ccByUsername.collect().mkString("\n"))
        
    }
}

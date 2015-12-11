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

        val inputFilePath = args(0)
        val outputFilePath = args(1)

        val conf = new SparkConf()
        conf.set("spark.driver.memory", "1g")
        conf.set("spark.eventLog.enabled", "true")
        conf.set("spark.eventLog.dir", "/home/ubuntu/storage/logs")
        conf.set("spark.executor.memory", "21000m")
        conf.set("spark.executor.cores", "4")
        conf.set("spark.task.cpus", "1")
        val sc = new SparkContext(conf)

        // Load the graph as in the PageRank example
        val graph = GraphLoader.edgeListFile(sc, inputFilePath)
        // Find the connected components
        val cc = graph.connectedComponents().vertices

        // Save to HDFS (similar to giraph)
        cc.saveAsTextFile(outputFilePath)

        // println(cc.collect().mkString("\n"))

    }
}

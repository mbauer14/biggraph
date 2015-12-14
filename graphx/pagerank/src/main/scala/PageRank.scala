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
        val startMillis = System.currentTimeMillis
        val appName = "CS-838-Final-PageRank"
        val master = "spark://10.0.1.56:7077"

        // Open correct file from HDFS, supplied as first arg
        val inputLocation = args(0)
        val outputFilePath = args(1)

        val conf = new SparkConf()
        conf.set("spark.driver.memory", "1g")
        conf.set("spark.eventLog.enabled", "true")
        conf.set("spark.eventLog.dir", "/home/ubuntu/storage/logs")
        conf.set("spark.executor.memory", "21000m")
        conf.set("spark.executor.cores", "4")
        conf.set("spark.task.cpus", "1")

        val startSetup = System.currentTimeMillis
        val sc = new SparkContext(conf)

        // Load the edges as a graph
        val graph = GraphLoader.edgeListFile(sc, inputLocation)
        val setupTime = System.currentTimeMillis - startSetup
        // Run PageRank
        val ranks = graph.pageRank(0.0001).vertices
       
        // Save to HDFS
        val startFinish = System.currentTimeMillis
        ranks.saveAsTextFile(outputFilePath)
        val finishTime = System.currentTimeMillis - startFinish

        println(s"SETUP_TIME: $setupTime")
        println(s"FINISH_TIME: $finishTime")
        println(s"START_MILLIS: $startMillis")
        //print the result
        //println(ranks.collect().mkString("\n"))

    }
}

/*** SimpleApp.scala ***/
import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.graphx.util.GraphGenerators
import scala.collection.mutable.ArrayBuffer


object SSSP {

    def main(args: Array[String]) {
        val startMillis = System.currentTimeMillis
        val appName = "CS-838-FinalGraphX-SSSP"
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
        val startSetup = System.currentTimeMillis
        val sc = new SparkContext(conf)

        val graph = GraphLoader.edgeListFile(sc, inputFilePath)
        val setupTime = System.currentTimeMillis - startSetup
        val sourceId: VertexId = 0 // The ultimate source

        val initialGraph = graph.mapVertices((id, _) => if (id == sourceId) 0.0 else Double.PositiveInfinity)
        val sssp = initialGraph.pregel(Double.PositiveInfinity)(
            (id, dist, newDist) => math.min(dist, newDist), // Vertex Program
            triplet => {  // Send Message
                if (triplet.srcAttr + triplet.attr < triplet.dstAttr) {
                    Iterator((triplet.dstId, triplet.srcAttr + triplet.attr))
                } else {
                    Iterator.empty
                }
            },
            (a,b) => math.min(a,b) // Merge Message
        )
        
        // Save to HDFS (similar to giraph)
        val startFinish = System.currentTimeMillis
        sssp.vertices.saveAsTextFile(outputFilePath)
        val finishTime = System.currentTimeMillis - startFinish
        
        println(s"SETUP_TIME: $setupTime")
        println(s"FINISH_TIME: $finishTime")
        println(s"START_MILLIS: $startMillis")

        //println(sssp.vertices.collect.mkString("\n"))
    }
}

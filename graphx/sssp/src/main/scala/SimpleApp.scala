/*** SimpleApp.scala ***/
import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import scala.collection.mutable.ArrayBuffer


object SimpleApp {
    def mostPopular(a: (VertexId, (Long, Int)), b: (VertexId, (Long, Int))): (VertexId, (Long, Int)) = {
        /*
            Reduce phase which combines all (vertexID, (NumWords, Degrees)) tuples
            Takes max degrees element.
                If tie, take element with more words

            ._2 is the (NumWords, Degrees) tuple
        */
       //If degrees of a is greater than degrees of b, return a
        if (a._2._2 > b._2._2) {
            a
        }
        else if (a._2._2 == b._2._2 && a._2._1 > b._2._1) {
            //If degrees are equal and a words > b words, return a
            a
        }
        else {
            //All other cases, return b
            b
        }
    }

    def averageNeighbors(tuple: (VertexId, Array[(VertexId, Long)])): (VertexId, Float) = {
        
        /*
            Map phase with takes a vertexID (time interval) and array of neighbors with word counts
            Calculates the average of all neighbors word counts
        */
        var vertId = tuple._1
        var neighbors = tuple._2
        var numNeighbors = 0.toLong
        var sumNeighbors = 0.toLong

        for ((vId, numWords) <- neighbors) {
            sumNeighbors = sumNeighbors + numWords
            numNeighbors = numNeighbors + 1
        }

        //Handle potential overflow
        if (numNeighbors > 0) {
            (vertId, (sumNeighbors.toFloat / numNeighbors.toFloat) )
        }
        else {
            (vertId, 0.toFloat)
        }
    }
    
    def edgemax(e1: Edge[Long], e2: Edge[Long]): Edge[Long] = {
        /*
            Reduce phase which takes the max edge count (e._3)
         */
        //If degrees of a is greater than degrees of b, return a
        if (e1.attr > e2.attr) {
            e1
        }
        else {
            e2
        }
    }


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

        // The number of time intervals
        val NumBatches = 200

        //Load in the input RDDs from each file
        //Expecting file to consist of just lines
        val inputRDDs = new Array[RDD[String]](NumBatches)
        // Create the RDDS for each 
        for (i <- 0 to NumBatches-1) {
            println("i: " + i)
            inputRDDs(i) = sc.textFile("parsed/" + i + "-word_counts.txt")
        }

        //For each RDD
        //Loop over all RDDs with time interval > current time interval
        //Create vertices (value is the number of words in the interval)
        //Test for common values with intersection between two RDDs
        //If common values (intersection cardinality > 0), then create edge between vertices
        //Edge attribute is the number of shared vertices
        var preEdges = ArrayBuffer[Edge[Long]]()
        var preVertices = new Array[(VertexId, Long)](NumBatches)
        val i = 0
        var j = 0
        var sharedCount = 0.toLong
        for (i <- 0 to NumBatches-1) {
            j = 0
            //Add the vertex
            preVertices(i) = (i.toLong, inputRDDs(i).count())
            for (j <- i+1 to NumBatches-1) {
                sharedCount = inputRDDs(i).intersection(inputRDDs(j)).count()
                if (sharedCount != 0) {
                    //Add edge in both directions so we have "undirected graph"
                    preEdges += Edge(i.toLong, j.toLong, sharedCount)  
                }
            }
        }

        //BUILD THE ACTUAL GRAPH OUT OF ALL THE ABOVE INFORMATION
        val vertices: RDD[(VertexId, Long)] = sc.parallelize(preVertices)
        val edges: RDD[Edge[Long]]= sc.parallelize(preEdges.toSeq)
        val graph = Graph(vertices, edges)

        println("ALL TRIPLETS.............")
        graph.triplets.collect.foreach(println(_))

        /*
            Question 1: Find the number of edges where the number of words in the source vertex is strictly larger than the number of words in the destination vertex.
            Create triplets and filter by src word Count > dst word Count
        */

        println(".....................QUESTION 1......................")
        println("Find the number of edges where the number of words in the source vertex is strictly larger than the number of words in the destination vertex.")
        val tripletsQuestion1 = graph.triplets.filter(triplet => triplet.srcAttr > triplet.dstAttr)
        //tripletsQuestion1.collect().foreach(println(_))
        val question1Answer = tripletsQuestion1.count() 
        println("....................Question1 answer: " + question1Answer)

        
        println(".....................QUESTION 2......................")
        println("Find the most popular vertex. A vertex is the most popular if it has the most number of edges to his neighbors and it has the maximum number of words.")
        //Join the vertices with the degree of each vertex
        //Pass this new VertexRDD to the mostPopular reduce function
        val vertsDegrees = graph.vertices.innerJoin(graph.degrees) {(vid, a, b) => (a, b)} 
        val question2Answer = vertsDegrees.reduce(mostPopular)
        println("....................Question2 answer: " + question2Answer)
        
        
        println(".....................QUESTION 3......................")
        println("Find the average number of words in every neighbor of a vertex.")
        //Simply get all neighbors of each node, then send to a map function which computes average for each
        val averageNeighborDegrees = graph.ops.collectNeighbors(EdgeDirection.Either).map(averageNeighbors).collect()
        //This will print out the vertexId, average pairs
        println("....................Question3 answer: ")
        

        println(".....................QUESTION 4......................")
        println("Find the time interval whose tweets share the most number of words with tweets from any other interval.")
        //Get edges, and reduce to find the edge with the greatest value. Simple max reduce function
        val maxEdge = graph.edges.reduce(edgemax)
        //This will print out the vertexId, average pairs
        println("....................Question4 answer: ")
        println("maxInterval (batch1, batch2, sharedWords)= " + maxEdge)
        

        graph.vertices.collect().foreach(println(_))

        //Put the count into the edge, do the same reduce max for question 2

        
    }
}

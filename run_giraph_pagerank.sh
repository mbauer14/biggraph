#!/bin/sh
echo "Start: " $(($(date +%s%N)/1000000))
hadoop jar giraph/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar org.apache.giraph.GiraphRunner -D giraph.useOutOfCoreGraph=true org.apache.giraph.examples.SimplePageRankComputation -vif org.apache.giraph.io.formats.JsonLongDoubleFloatDoubleVertexInputFormat -vip /final/$1/$1_giraph.txt -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat -op $2 -w 4 -yj giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar -ca mapred.job.tracker=10.0.1.56:5431 -mc org.apache.giraph.examples.SimplePageRankComputation\$SimplePageRankMasterCompute 
echo "End: " $(($(date +%s%N)/1000000))

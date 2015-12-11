echo "Start: " $(date +%s)
hadoop jar giraph/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar org.apache.giraph.GiraphRunner org.apache.giraph.examples.ConnectedComponentsComputation -vif org.apache.giraph.io.formats.IntIntNullTextInputFormat -vip /final/$1/$1_giraph_cc.txt -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat -op /final/$1/$2 -w 4 -yj giraph/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar -ca mapred.job.tracker=10.0.1.56:5431
echo "End: " $(date +%s)


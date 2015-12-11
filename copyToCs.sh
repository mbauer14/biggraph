# GIRAPH RELATED STUFF
rsync -avzC giraph/*.sh giraph/munged giraph/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar $1@best-linux.cs.wisc.edu:~/final/giraph/

# UTILS RELATED STUFF
rsync -avzC run.py runutils *.sh $1@best-linux.cs.wisc.edu:~/final/

# GRAPHX RELATED STUFF
rsync -avzC graphx/pagerank/target/scala-2.10/graphx-pagerank_2.10-1.0.jar graphx/wcc/target/scala-2.10/graphx-wcc_2.10-1.0.jar graphx/sssp/target/scala-2.10/graphx-sssp_2.10-1.0.jar $1@best-linux.cs.wisc.edu:~/final/graphx/

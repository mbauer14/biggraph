# GIRAPH RELATED STUFF
#rsync -avzC giraph/*.sh giraph/munged giraph/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar cloudlab:~/final/giraph/

# UTILS RELATED STUFF
rsync -avzC run.py runutils *.sh cloudlab:~/final/

# GRAPHX RELATED STUFF
rsync -avzC graphx/graphx-pagerank_2.10-1.0.jar graphx/graphx-wcc_2.10-1.0.jar graphx/graphx-sssp_2.10-1.0.jar cloudlab:~/final/graphx/

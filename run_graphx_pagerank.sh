echo "Start: " $(date +%s)
spark-submit graphx/graphx-pagerank_2.10-1.0.jar /final/$1/$1_graphx.txt /final/$1/$2
echo "End: " $(date +%s)

#!/bin/sh
echo "Start: " $(date +%s)
spark-submit graphx/graphx-wcc_2.10-1.0.jar /final/$1/$1_graphx.txt $2
echo "End: " $(date +%s)

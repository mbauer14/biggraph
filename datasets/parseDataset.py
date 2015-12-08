def readInLines(name):
    with open(name) as f:
      return f.readlines()

def outputFile(name):
   output_file = open(name, "w")
   source_value = 1
   edge_value = 1
   for source in graph:
       output_file.write("[" + str(source) + "," + str(source_value) + ",[")
       i = 0
       for dest in graph[source]:
           if i != len(graph[source]) - 1:
               output_file.write("[" + str(dest) + "," + str(edge_value) + "],")
           else:
               output_file.write("[" + str(dest) + "," + str(edge_value) + "]")
           i += 1
       output_file.write("]]\n")
   output_file.close()

def outputFileConnectedComponents(name):
   output_file = open(name, "w")
   for source in graph:
       output_file.write(str(source) + " ")
       for dest in graph[source]:
           output_file.write(str(dest) + " ")
       output_file.write("\n")
   output_file.close()

# IMPORTANT: This will output an undirected graph. The number of edges
# will be double what is indicated online

if __name__ == '__main__':
   content = readInLines("livejournal/soc-LiveJournal1.txt")
   graph = {}
   for line in content:
       if line[0] == '#':
           continue
       nodes = line.split()
       source = nodes[0]
       dest = nodes[1]
       if source in graph:
           graph[source].append(dest)
       else:
           newEdges = []
           newEdges.append(dest)
           graph[source] = newEdges

       if dest in graph:
           graph[dest].append(source)
       else:
           newEdges = []
           newEdges.append(source)
           graph[dest] = newEdges

   print "Nodes: " + str(len(graph))
   edges = 0
   for key in graph:
     for dest in graph[key]:
         edges += 1

   print "Edges: " + str(edges)
   #outputFile("gnutella/gnutella_giraph.txt") 
   outputFileConnectedComponents("livejournal/livejournal_giraph_cc.txt") 

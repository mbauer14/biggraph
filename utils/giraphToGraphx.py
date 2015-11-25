a = """
[0,0,[[1,1],[3,3]]]
[1,0,[[0,1],[2,2],[3,1]]]
[2,0,[[1,2],[4,4]]]
[3,0,[[0,3],[1,1],[4,4]]]
[4,0,[[3,4],[2,4]]]
"""
vertices = []
edges = []
for line in a.split():
    source_id, source_weight, vertEdges = eval(line)
    vertices.append((source_id, source_weight))
    for edge in vertEdges:
        edges.append((source_id, edge[0], edge[1]))


print("Vertices: {}".format(vertices))
print("Edges: {}".format(edges))

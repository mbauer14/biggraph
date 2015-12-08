import sys

def readInput(inputpath):
    with open(inputpath) as f:
        return f.readlines()

def outputToFile(outputpath, edges):
    with open(outputpath, 'w') as f:
        for edge in edges:
            f.write(" ".join(edge) + "\n")

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        filepath = args[1]
        inputpath = filepath + "_giraph.txt"
        outputpath = filepath + "_graphx.txt"
        print("Converting {} to {}".format(inputpath, outputpath))

        lines = readInput(inputpath)

        vertices = []
        edges = []
        for line in lines:
            source_id, source_weight, vertEdges = eval(line)
            vertices.append((source_id, source_weight))
            for edge in vertEdges:
                edges.append([str(source_id), str(edge[0])])


        for v in vertices:
            print v
            if v[1] != 1:
                print "not zero!"
        print edges

        outputToFile(outputpath, edges)

    else:
        print("Error - supply the correct dataset")

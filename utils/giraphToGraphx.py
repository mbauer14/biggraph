import sys

def readInput(inputpath):
    with open(inputpath) as f:
        return f.readlines()

def outputToFile(outputpath, edges):
    totalEdges = len(edges)
    currEdges = 0
    with open(outputpath, 'w') as f:
            currEdges += 1
            if currEdges % 1000 == 0:
                print("completed ({}/{}) lines".format(currEdges, totalEdges))


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        datatype = args[1]
        inputpath = "datasets/{}/{}_giraph.txt".format(datatype, datatype)
        outputpath = "datasets/{}/{}_graphx.txt".format(datatype, datatype)
        print("Converting {} to {}".format(inputpath, outputpath))

        f_in = open(inputpath)
        f_out = open(outputpath, 'w')

        vertices = []
        currLines = 0
        # Read in line by line, output all edges
        for line in f_in:
            edges = []
            source_id, source_weight, vertEdges = eval(line)
            for edge in vertEdges:
                edges.append([str(source_id), str(edge[0])])

            currLines += 1

            if currLines % 1000 == 0:
                print("completed {} lines".format(currLines))

            # Output
            for edge in edges:
                f_out.write(" ".join(edge) + "\n")


        f_in.close()
        f_out.close()

    else:
        print("Error - supply the correct dataset")

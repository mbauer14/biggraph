#!/usr/bin/python
import subprocess
from runutils import procutils
from runutils import sparkutils
from runutils import mrutils
import os
import json
import pprint
import datetime
# ACTUAL
#types = ['giraph', 'graphx']
#datasets = ['gnutella', 'google', 'livejournal']
#algos = ['sssp', 'wcc', 'pagerank']

xtypes = ['giraph', 'graphx']
datasets = ['tiny']
algos = ['sssp']
NUM_ITERS = 1

vms = ['vm-1', 'vm-2', 'vm-3', 'vm-4']


def callRunScript(xtype, algo, dataset, logfile, hdfsPath, name):
    script = './run_{}_{}.sh'.format(xtype, algo)
    print 'Running script: %s > %s' % (script, logfile)
    f = open(logfile, 'w')
    subprocess.call([script, dataset, os.path.join(hdfsPath, name)], stdout=f)


def output_to_file(resultFile, results):
    if os.path.exists(resultFile):
        os.remove(resultFile)

    with open(resultFile, 'w') as outfile:
        json.dump(results, outfile)

    print('resultFile: {}'.format(resultFile))
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(results)

def emptyBufferCaches():
    # Execute ssh command, get results
    for vm in vms:
        cat_output = subprocess.check_output(['ssh', vm, './clear_cache.sh'])

def hadoopMakeDirs(hdfsPath):
    subprocess.call(['hadoop', 'dfs', '-mkdir', hdfsPath])

def runAlgo(resultsDir, hdfsPath, xtype, algo, dataset, iterationNo):
    """
        Runs a specific algorithm on the specific framework.
        Stores results to HDFS in both cases

        currtime = human readable date/time for formatting output
        xtype = graph processing system (giraph/graphx)
        algo = type of algorithm to run (connected components, sssp, pagerank)
        dataset = what kind of dataset to run (preprocessed and available in HDFS)
    """
    # Get the initial stats for all vms
    print 'getting initial stats'
    start_stats = procutils.get_all_stats()
    print 'initial stats complete'

    #Create all the paths
    name = '_'.join([str(a) for a in [xtype, algo, dataset, iterationNo]])
    logfile = os.path.join(resultsDir, 'logs', name)
    xoutputdir = os.path.join(resultsDir, 'xoutput', name)
    resultfile = os.path.join(resultsDir, 'data', name)

    # Will call the script that performs the query, output the result of that query to a file
    print 'logfile: %s' % logfile

    print 'running script!'
    callRunScript(xtype, algo, dataset, logfile, hdfsPath, name)
    print 'script complete'

    # Get the final stats
    print 'Getting final stats.'
    stop_stats = procutils.get_all_stats()
    print 'Final stats complete.'

    # Calculate the differences between
    print 'Calculating diff_stats'
    diff_stats = procutils.calc_stats_diff(start_stats, stop_stats)
    print 'Finishing diff_stats'

    time_elapsed = procutils.read_time_stamps(logfile)

    print 'get_task_stats start'
    if (xtype == 'giraph'):
        total_num_tasks, ratio_tasks, task_distribution = mrutils.get_task_stats(xoutputdir)
    else:
        total_num_tasks, ratio_tasks, task_distribution = sparkutils.get_task_stats(xoutputdir)
    print 'get_task_stats finish'

    results = {'disknet': diff_stats,
                'time_elapsed': time_elapsed,
                'total_num_taks': total_num_tasks,
                'ratio_tasks': ratio_tasks,
                'task_distribution': task_distribution
            }

    # Echo everything to a file
    output_to_file(resultfile, results)


def main():
    # Get current time to save results
    currtime = str(datetime.datetime.now()).replace("-", "_").replace(" ", "-").replace(":", "_")
    currtime = currtime[:currtime.find(".")]

    print("currtime: {}".format(currtime))
    # Make the directory which will hold all results
    resultsDir = os.path.join("results", "{}-iters_{}".format(currtime, NUM_ITERS))
    dataDir = os.path.join(resultsDir, 'data')
    logDir = os.path.join(resultsDir, 'logs')
    xOutputDir = os.path.join(resultsDir, 'xoutput')
    os.makedirs(resultsDir)
    os.makedirs(dataDir)
    os.makedirs(logDir)
    os.makedirs(xOutputDir)

    hdfsPath = "/final/{}-iters{}".format(currtime, NUM_ITERS)
    hadoopMakeDirs(hdfsPath)

    for iterationNo in range(0, NUM_ITERS):
        for algo in algos:
            for dataset in datasets:
                for xtype in xtypes:
                    emptyBufferCaches()
                    sparkutils.removeLocalDirs()
                    print("{} iter {}: starting {} {} {}".format(currtime, iterationNo, xtype, algo, dataset))
                    runAlgo(resultsDir, hdfsPath, xtype, algo, dataset, iterationNo)


if __name__ == "__main__":
    main()

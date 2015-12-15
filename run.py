#!/usr/bin/python
import subprocess
from runutils import procutils
from runutils import sparkutils
from runutils import mrutils
import os
import json
import pprint
import datetime
import threading
import time
# ACTUAL

#xtypes = ['giraph', 'graphx']
#datasets = ['tiny']
#algos = ['sssp', 'cc', 'pagerank']

xtypes = ['giraph', 'graphx']
datasets = ['gnutella', 'google', 'livejournal']
algos = ['sssp', 'cc', 'pagerank']

NUM_ITERS = 1

vms = ['vm-1', 'vm-2', 'vm-3', 'vm-4']

# DONE - place here when done!
# Remove anything in ~/logs/apps/ before each run
# Get setup and total time in giraph (from ~/logs/apps/
# Add setup time measurement, calculation time to 3 graphx queries
# Get setup time from graphx

#TODO - do these and you're done!
# Detect a failed query
# Return the start time, calculate all that business


def callRunScript(xtype, algo, dataset, logfile, hdfsPath, name):
    script = './run_{}_{}.sh'.format(xtype, algo)
    print 'Running script: %s > %s' % (script, logfile)
    f = open(logfile, 'w')
    isFail = True

    startTime = int(time.time())
    runProcess = subprocess.Popen([script, dataset, os.path.join(hdfsPath, name)], stdout=f, stderr=f, shell=True)
    currTime = int(time.time())
    # Let queries run for 200 seconds
    while (int(time.time()) - startTime) < 200:
        runProcess.poll()
        if runProcess.returncode:
            print("process completed!")
            isFail = False
            break

        time.sleep(1)

    if isFail:
        runProcess.terminate()

    return isFail

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

def clearAppLogs():
    # Remove all files from ~/logs/apps/
    for vm in vms:
        output = subprocess.check_output(['ssh', vm, 'rm', '-rf', '/home/ubuntu/logs/apps/*'])

def copyLogsFromVms():
    for vm in vms:
        if vm != 'vm-1':
            vmLoc = "{}:/home/ubuntu/logs/apps/*".format(vm)
            output = subprocess.check_output(['scp', '-r', vmLoc, '/home/ubuntu/logs/apps/'])

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
    loop_stats = procutils.StatsLooper()
    loop_stats.start()
    print 'initial stats complete'

    #Create all the paths
    name = '_'.join([str(a) for a in [xtype, algo, dataset, iterationNo]])
    logfile = os.path.join(resultsDir, 'logs', name)
    xoutputdir = os.path.join(resultsDir, 'xoutput', name)
    resultfile = os.path.join(resultsDir, 'data', name)

    # Will call the script that performs the query, output the result of that query to a file
    print 'logfile: %s' % logfile

    print 'running script!'
    isFail = callRunScript(xtype, algo, dataset, logfile, hdfsPath, name)
    print 'script complete'

    fail_time = None
    if isFail:
        print("Failed (timed out).")
        fail_time = int(time.time())

    # Get the final stats
    print 'Getting final stats.'
    stop_stats = procutils.get_all_stats()
    print 'Final stats complete.'

    # Calculate the differences between
    print 'Calculating diff_stats'
    diff_stats = procutils.calc_stats_diff(start_stats, stop_stats)
    print 'Finishing diff_stats'

    # Get elapsed time
    print("get elapsed time, cpumem")
    start_time, end_time = procutils.read_time_stamps(logfile, end_time=fail_time)
    cpuMemVals = loop_stats.cpuMemStats
    maxMem = loop_stats.maxMem
    loop_stats.signal = False
    print("finished elapsed time, cpumem")

    # Get setup time/other time
    if xtype == 'giraph':
        copyLogsFromVms()
        times = mrutils.get_times()
    else:
        times = sparkutils.get_times(logfile)

    # Change times in the cpuMemVals to "query time", not abs time
    for entry in cpuMemVals:
        entry['time'] = entry['time'] - start_time

    results = {
        'disknet': diff_stats,
        'total_time_elapsed': total_time_elapsed,
        'maxMem': maxMem,
        'cpuMem': cpuMemVals,
        'times': times,
        'isSuccess': !isFail
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
                    clearAppLogs()
                    sparkutils.removeLocalDirs()
                    print("{} iter {}: starting {} {} {}".format(currtime, iterationNo, xtype, algo, dataset))
                    runAlgo(resultsDir, hdfsPath, xtype, algo, dataset, iterationNo)


if __name__ == "__main__":
    main()

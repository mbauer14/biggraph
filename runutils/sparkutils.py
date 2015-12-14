from __future__ import division
import json
import glob
import shutil
import subprocess
import os

vms = ['vm-1', 'vm-2', 'vm-3', 'vm-4']

def removeLocalDirs():
    print("Removing all local spark dirs")
    for vm in vms:
        cat_output = subprocess.check_output(['ssh', vm, 'rm', '-rf', '/home/ubuntu/storage/data/spark/rdds_map/*'])


def get_times(filepath):
    """
        Parses file to find setup time and close time
        Setup includes setup/load input to HDFS, closing is just from logs
        setup = init + setup + input superstep
        close = shutdown
        startMillis = start time
    """
    pattern = dict()
    pattern['setup'] = re.compile('SETUP_TIME: ([0-9]+)')
    pattern['finish'] = re.compile('FINISH_TIME: ([0-9]+)')
    pattern['startMillis'] = re.compile('START_MILLIS: ([0-9]+)')
    print("filepath: {}".format(filepath))
    with open(filepath) as f:
        lines = f.readlines()

    found= {key:False for key in pattern.keys()}
    results = dict()

    for l in lines:
        for key in found.keys():
            if not found[key]:
                match = re.finditer(pattern[key], l)
                for m in match:
                    results[key] = m.group(1)
                    found[key] = True

    return results

def getEventLogFile(xoutputdir):
    xoutputname = xoutputdir + '_spark'
    print("Getting event log file")
    output = glob.glob('/home/ubuntu/storage/logs/*.inprogress')
    filepath = output[0]
    with open(filepath) as f:
        content = f.readlines()

    # move the file
    shutil.copy(filepath, xoutputname)

    # Remove all files
    print("removing all log files")
    for o in output:
        os.remove(o)
    return content

def get_task_stats(xoutputdir):

    content = getEventLogFile(xoutputdir)

    a= []
    for i in content:
        a.append(json.loads(i))

    task_dist = []
    read_count = 0
    aggregate_count = 0

    for i,j in zip(a, xrange(0,len(a))) :

        if u'Event' in i.keys():
            if i[u'Event'] == u'SparkListenerTaskEnd' and i['Task End Reason']['Reason'] == 'Success':
                if u'Input Metrics' in i['Task Metrics']:
                    read_count += 1
                else:
                    aggregate_count += 1

                task_dist.append({'start_time': i['Task Info']['Launch Time'], 'end_time': i['Task Info']['Finish Time']})

    total_tasks = read_count + aggregate_count
    ratio = aggregate_count/read_count
    return total_tasks, ratio, task_dist


#b = parse_data('example_21')

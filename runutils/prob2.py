from pyspark import SparkContext, SparkConf
from pyspark.sql import HiveContext
import subprocess
import procutils
import os
import glob
import time
from spark_script import parse_data

vms = ['vm-1', 'vm-2', 'vm-3', 'vm-4']

def setupHiveContext():
    appName = 'CS-838-Assignment2-Question2'
    master = 'spark://10.0.1.56:7077' 

    # Setup all the configuration stuff
    conf = SparkConf()
    conf.setAppName(appName)
    conf.setMaster(master)
    conf.set('spark.driver.memory', '1g')
    conf.set('spark.eventLog.enabled', True)
    conf.set('spark.eventLog.dir', '/home/ubuntu/storage/logs')
    conf.set('spark.executor.memory', '21000m')
    conf.set('spark.executor.cores', '4')
    conf.set('spark.task.cpus', '1')

    sc = SparkContext(conf=conf)
    hiveContext = HiveContext(sc)
    return hiveContext

def getThriftServerPid():
    FNULL = open(os.devnull, 'w')
    c1 = ['netstat', '-nlp']
    p1 = subprocess.Popen(c1, stdout=subprocess.PIPE, stderr=FNULL)

    c2 = ['grep', '10000']
    p2 = subprocess.Popen(c2, stdin=p1.stdout, stdout=subprocess.PIPE)
    result = p2.stdout.read()
    outputArray = result.split()
    if len(outputArray) > 0:
        portAndJava = outputArray[-1]
        indexOfSlash = portAndJava.index('/')
        port = portAndJava[0:indexOfSlash]
        return port
    return None

def killThriftServer(pid):
    if pid is not None:
        print "Killing Thrift Server"
        subprocess.call(['kill', pid])
        waitForThriftServerToDie()
        return
    print "Thrift Server is already down"

def waitForThriftServerToDie():
    print "Waiting for Thrift server to die..."
    while getThriftServerPid() is not None:
        print "Sleeping 5 seconds"
        time.sleep(5)
    print "Thrift server is dead!"

def emptyBufferCaches():
    print "Emptying all buffer caches"
    for vm in vms:
    # Execute ssh command, get results
        cat_output = subprocess.check_output(['ssh', vm, './clear_cache.sh'])  

def executeQuery(hiveContext, persistOutput):
    
    actualQuery = """
    select  i_item_desc 
          ,i_category 
          ,i_class 
          ,i_current_price
          ,i_item_id
          ,sum(ws_ext_sales_price) as itemrevenue 
          ,sum(ws_ext_sales_price)*100/sum(sum(ws_ext_sales_price)) over
              (partition by i_class) as revenueratio
    from	
        web_sales
            ,item 
            ,date_dim
    where 
        web_sales.ws_item_sk = item.i_item_sk 
        and item.i_category in ('Jewelry', 'Sports', 'Books')
        and web_sales.ws_sold_date_sk = date_dim.d_date_sk
        and date_dim.d_date between '2001-01-12' and '2001-02-11'
    group by 
        i_item_id
            ,i_item_desc 
            ,i_category
            ,i_class
            ,i_current_price
    order by 
        i_category
            ,i_class
            ,i_item_id
            ,i_item_desc
            ,revenueratio
    limit 100
            """
    currTime = time.time()
    results = hiveContext.sql(actualQuery)
    results.collect()
    currTime2 = time.time()
    if persistOutput:
        results.cache()
    diff = currTime2 - currTime
    return diff, results

def getEventLogFile():
    print "Getting event log file"
    output = glob.glob('/home/ubuntu/storage/logs/*.inprogress')
    return output[0]

def runQuery(hiveContext, persist, filename, old_lines = 0):
    # Get the initial stats for all vms
    print 'Getting initial stats.'
    start_stats = procutils.get_all_stats() 
    print 'Initial stats complete.'

    print 'Running Query 12'
    time_elapsed, resultsRDD = executeQuery(hiveContext, persist)
    print 'Finished running query'

    # Get the final stats
    print 'Getting final stats.'
    stop_stats = procutils.get_all_stats()
    print 'Final stats complete.'

    # Calculate the differences between 
    print 'Calculating diff_stats'
    diff_stats = procutils.calc_stats_diff(start_stats, stop_stats)
    print 'Finishing diff_stats'

    eventLogFileName = getEventLogFile()
    total_num_tasks, lines = parse_data(eventLogFileName, old_lines)
    #os.remove(eventLogFileName)
   
    results = {'disknet': diff_stats,
                'time_elapsed': time_elapsed,
                'total_num_task': total_num_tasks,
                #'ratio_tasks': ratio_tasks,
                #'task_dist': task_dist
    }

    output_to_file(results, filename)
    return resultsRDD, lines

def runPersistedQuery(resultsRDD, filename, old_lines):
    # Get the initial stats for all vms
    print 'Getting initial stats.'
    start_stats = procutils.get_all_stats() 
    print 'Initial stats complete.'

    print 'Running Query 12'
    currTime = time.time()
    resultsRDD.collect()
    currTime2 = time.time()
    time_elapsed = currTime2 - currTime
    print 'Finished running query'

    # Get the final stats
    print 'Getting final stats.'
    stop_stats = procutils.get_all_stats()
    print 'Final stats complete.'

    # Calculate the differences between 
    print 'Calculating diff_stats'
    diff_stats = procutils.calc_stats_diff(start_stats, stop_stats)
    print 'Finishing diff_stats'

    total_num_tasks, lines = parse_data(getEventLogFile(), old_lines)
   
    results = {'disknet': diff_stats,
                'time_elapsed': time_elapsed,
                'total_num_task': total_num_tasks,
                #'ratio_tasks': ratio_tasks,
                #'task_dist': task_dist
    }

    output_to_file(results, filename)
    return resultsRDD


def output_to_file(results, filename):
    filepath = './plotdata/problem2-query12-%s' % (filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    import json
    with open(filepath, 'w') as outfile:
        json.dump(results, outfile)

    import pprint 
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(results)

if __name__ == "__main__":
    killThriftServer(getThriftServerPid())
    hiveContext = setupHiveContext()
    emptyBufferCaches()
    
    useQuery = """
    USE tpcds_text_db_1_50
               """
    hiveContext.sql(useQuery)

    # Cache the inputs on the first runthrough
    # This only affects the second Run, the first run will exhibit no caching behavior
    hiveContext.cacheTable("web_sales")
    hiveContext.cacheTable("item")
    hiveContext.cacheTable("date_dim")
    results, lines = runQuery(hiveContext, False, "nocaching")

    #After the first run, the input tables will be cached 
    #On this second run, cache the outputs (for the 3rd run)
    results, lines = runQuery(hiveContext, True, "cacheinputs", lines)

    #On this third run, we want to just rerun to take advantage of  
    runPersistedQuery(results, "cacheboth", lines)

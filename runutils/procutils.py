import json
import subprocess


vms = ['vm-1', 'vm-2', 'vm-3', 'vm-4']


def parse_net(a):
    """
    Takes the output of /proc/net/dev and returns receive_byte
    and transmit_byte as a tuple

    Args:
        s: the output of /proc/net/dev

    Returns:
        tuple (sectors_read, sectors_written)    
    """
    receive_byte =  int(a[2].split()[1])
    transmit_byte = int(a[2].split()[9])
    d = {
            'receive_bytes': receive_byte,
            'transmit_bytes': transmit_byte
        }
    return d



def parse_disk(a):
    """
    Takes the output of /proc/diskstats and returns sectors read
    and sectors_written as a tuple

    Args:
        s: the output of /proc/net/dev

    Returns:
        tuple (sectors_read, sectors_written)

    """
    sectors_read =  int(a[len(a)-2].split()[5])
    sectors_written = int(a[len(a)-2].split()[9])
    bytes_read = sectors_read * 512
    bytes_written = sectors_written * 512
    d = {
            'read_bytes': bytes_read,
            'write_bytes': bytes_written
        }
    return d


def read_time_stamps(filename):
    """
    Takes in filename, reads it and outputs a tuple of start time 
    and end time

    Args:
        filename : name of file

    Returns:
        tuple (Start time, end time)
    """

    with open(filename) as f:
        a = f.readlines()
        start_time = int(a[0].split()[1])
        end_time = int(a[len(a)-1].split()[1])
        elapsed_time = end_time - start_time
        return elapsed_time

def ssh_machine_proc_stats(hostname, filepath):
    """
        Uses ssh command to execute a cat, get info for specific filepath
    """ 
    # Execute ssh command, get results
    cat_output = subprocess.check_output(['ssh', hostname, 'cat', filepath])  
    return cat_output

def get_machine_proc_stats(hostname, filepath):
    """
        Gets the proc stats for a specific machine and type 
    """
    cat_output = ssh_machine_proc_stats(hostname, filepath).split('\n')
    if 'disk' in filepath:
        parsed_stats = parse_disk(cat_output)
    else:
        parsed_stats = parse_net(cat_output)

    return parsed_stats

def get_all_stats():
    """
        Returns a dictionary of 

        {
            vm1:
                {
                    disk:
                        read:
                        write:
                    net:
                        receive:
                        transmit:
                },
            vm2:
                {
                    ...
                }
            vm3:
                {
                    ...
                },
            vm4:
                {
                    ...
                }
        }
    """
   
    all_stats = {}
     
    for vm in vms:
        all_stats[vm] = {'disk': {}, 'net': {}}
        all_stats[vm]['disk'] = get_machine_proc_stats(vm, '/proc/diskstats')
        all_stats[vm]['net'] = get_machine_proc_stats(vm, '/proc/net/dev')

    return all_stats


def calc_stats_diff(start_stats, stop_stats):
    """
         
    """
    diff_stats = {}

    for vm in vms:
        diff_stats[vm] = {'disk': {}, 'net': {}}
        diff_stats[vm]['disk']['read_bytes'] = stop_stats[vm]['disk']['read_bytes'] - start_stats[vm]['disk']['read_bytes']
        diff_stats[vm]['disk']['write_bytes'] = stop_stats[vm]['disk']['write_bytes'] - start_stats[vm]['disk']['write_bytes']
        diff_stats[vm]['net']['transmit_bytes'] = stop_stats[vm]['net']['transmit_bytes'] - start_stats[vm]['net']['transmit_bytes']
        diff_stats[vm]['net']['receive_bytes'] = stop_stats[vm]['net']['receive_bytes'] - start_stats[vm]['net']['receive_bytes']
        

    return diff_stats


if __name__ == "__main__":
    import pprint 
    import time
    print 'a'
    start = get_all_stats()
    print 'b'
    time.sleep(20)
    print 'c'
    stop = get_all_stats()
    print 'd'

    diff = calc_stats_diff(start, stop)
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(diff)

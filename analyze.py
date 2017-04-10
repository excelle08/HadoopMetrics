#!/usr/bin/python
from getopt import GetoptError, getopt
from config import config
from copy import deepcopy
from sys import argv
import os.path
import re
#import crash_on_ipy

decimal = re.compile(r'^\d+\.?\d*$')
integer = re.compile(r'^\d+$')

options = dict()


def parse(text, fields):
    time, content = text.split(' ', 1)
    content = content.split(': ')[1]
    time = int(time) // 1000  # Get seconds. Also use // for integer division
    items = content.split(', ')
    res = dict()
    for item in items:
        key, value = item.split('=')
        if key in fields:
            if integer.match(value):
                value = int(value)
            elif decimal.match(value):
                value = float(value)
            else:
                pass

            res[key] = value

    res['time'] = time
    return res


def help_info():
    print('Usage: %s --namenode [MetricName1,...] --datanode [MetricName1,...] <TaskName>' % argv[0])
    exit(0)


def extract_args(args):
    global options
    try:
        opts, argvs = getopt(args, 'an:d:', ['absolute', 'namenode=', 'datanode='])
        options['absolute'] = False
        for key, value in opts:
            if key in ('-d', '--datanode'):
                options['datanode_metrics'] = value.split(',')
            if key in ('-n', '--namenode'):
                options['namenode_metrics'] = value.split(',')
            if key in ('-a', '--absolute'):
                options['absolute'] = True

        options['task'] = argvs[0]

        options['namenode_host'] = config['master']
        options['datanode_host'] = config['slaves']

        #print 'Datanode Metrics: %s ' % ', '.join(options['datanode_metrics'])
        #print 'Namenode Metrics: %s ' % ', '.join(options['namenode_metrics'])
    except GetoptError, KeyError:
        help_info()


def compare_time(t1, t2):
    step = 5 # Currently we set the interval as 5 seconds
    return (t1 > t2 - step) and (t1 < t2 + step)


def compute_relative(metric_list):
    baseline = deepcopy(metric_list[0])
    for i in range(len(metric_list)):
        for key in baseline.keys():
            if isinstance(baseline[key], (int, float)):
                metric_list[i][key] -= baseline[key]


def compress_slave(master, slave):
    i = 0
    j = 0
    new_slave = list()
    while i < len(master) and j < len(slave):
        try:
            if compare_time(master[i]['time'], slave[j]['time']):
                new_slave.append(slave[j])
            elif master[i]['time'] > slave[j]['time']:
                i -= 1
            elif master[i]['time'] < slave[j]['time']:
                new_slave.append(slave[j])
                j -= 1
        finally:
            i += 1
            j += 1
    return new_slave


if __name__ == '__main__':
    extract_args(argv[1:])
    task = options['task']
    table = dict()
    csv = ''
    if not os.path.isdir(task):
        print('Task %s does not exist.' % task)
        exit(0)

    namenode = options['namenode_host']
    with open('%s/%s.namenode.out' % (task, namenode), 'r') as f:
        lines = f.readlines()
        table[namenode] = list()
        for line in lines:
            table[namenode].append(parse(line, options['namenode_metrics']))

    for datanode in options['datanode_host']:
        with open('%s/%s.datanode.out' % (task, datanode), 'r') as f:
            lines = f.readlines()
            table[datanode] = list()
            for line in lines:
                table[datanode].append(parse(line, options['datanode_metrics']))

    for host in options['datanode_host']:
        table[host] = compress_slave(table[namenode], table[host])       

    if not options['absolute']:
        compute_relative(table[namenode])
        for host in options['datanode_host']:
            compute_relative(table[host])
    
    aggregated_table = dict()

    for host in table.keys():
        for field in table[host][0].keys():
            if field not in aggregated_table:
                aggregated_table[field] = list() 
        for i in range(table[host].__len__()):
            for field, value in table[host][i].items():
                if i >= len(aggregated_table[field]):
                    aggregated_table[field].append(int(value))
                else:
                    if field == 'time' and host in datanode:
                        continue
                    aggregated_table[field][i] += int(value)
    
    #for host in table.keys():
    #    for field in table[host][0].keys():
    #        if not host == namenode and field == 'time':
    #            continue
    #        csv += '%s.%s,' % (host, field)
    #csv += '\r\n'
    
    fields = []
    for field in aggregated_table.keys():
        csv += '%s,' % field
        fields.append(field)
    csv += '\n'

    for i in range(len(aggregated_table[fields[0]])):
        for key in fields:
            csv += '%s,' % str(aggregated_table[key][i])
        csv += '\n';

    #for i in range(len(table[namenode])):
    #    for host in table.keys():
    #        index = i if (i < len(table[host])) else len(table[host]) - 1
    #        for k, value in table[host][index].items():
    #            if not host == namenode and k == 'time':
    #                continue
    #            csv += '%s,' % str(value)
    #    csv += '\r\n'

    print csv

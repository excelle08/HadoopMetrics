#!/usr/bin/python
from getopt import GetoptError, getopt
from config import config
from copy import deepcopy
from sys import argv
import os.path
import re

decimal = re.compile(r'^\d+\.?\d*$')
integer = re.compile(r'^\d+$')

options = dict()


def parse(text):
    time, content = text.split(' ', 1)
    content = content.split(': ')[1]
    time = int(time) // 1000  # Get seconds. Also use // for integer division
    items = content.split(', ')
    res = dict()
    for item in items:
        key, value = item.split('=')
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
    try:
        options, argvs = getopt(args, 'n:d:', ['namenode=', 'datanode='])
        for key, value in options:
            if key in ('-d', '--datanode'):
                options['datanode_metrics'] = value.split(',')
            if key in ('-n', '--namenode'):
                options['namenode_metrics'] = value.split(',')
        options['task'] = argvs[0]

        options['namenode_host'] = config['master']
        options['datanode_host'] = config['slaves']

        print 'Datanode Metrics: %s ' % ', '.join(options['datanode_metrics'])
        print 'Namenode Metrics: %s ' % ', '.join(options['namenode_metrics'])
    except GetoptError, KeyError:
        help_info()


def compare_time(t1, t2):
    step = 5 # Currently we set the interval as 5 seconds
    return (t1 > t2 - step) and (t1 < t2 + step)


def compute_relative(metric_list):
    baseline = deepcopy(metric_list[0])
    for i in range(len(metric_list)):
        for key in metric_list[i].keys():
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
            table[namenode].append(parse(line))

    for datanode in options['datanode_host']:
        with open('%s/%s.datanode.out' % (task, datanode), 'r') as f:
            lines = f.readlines()
            table[datanode] = list()
            for line in lines:
                table[datanode].append(parse(line))

    for host in options['datanode_host']:
        table[host] = compress_slave(table[namenode], table[host])       
        compute_relative(table[host])

    compute_relative(table[namenode])

    for host in table.keys():
        for field in table[host][0].keys():
            if not host == namenode and field == 'time':
                continue
            csv += '%s.%s,' % (host, field)
    csv += '\r\n'

    for i in range(len(table[namenode])):
        for host in table.keys():
            for value in table[host][i]:
                csv += '%s,' % str(value)
        csv += '\r\n'


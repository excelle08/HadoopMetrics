#!/usr/bin/env python3
from sys import argv
from csv import CSV
from getopt import getopt, GetoptError
from copy import deepcopy

config = dict()


def get_config(key, default=None):
    global config
    if key in config:
        return config[key]
    else:
        if default is not None:
            return default
        else:
            help()
            raise KeyError('Missing config key %s' % key)


def help():
    print ('Usage: %s [OPTiONS...]' % argv[0])
    print ('--prefix\t\t Prefix of hostnames')
    print ('--master\t\t ID of master machine')
    print ('--slaves\t\t IDs of slave machines')
    print ('--name\t\t Name of application')
    print ('--category-master\t\t Category in master')
    print ('--category-slave\t\t Category in slave')
    print ('--path\t\t Path')
    print ('--date\t\t Date of run. For the use of suffix')
    print ('--master-fields\t\t Master fields')
    print ('--slave-fields\t\t Slave fields')
    print ('--output\t\t Output file')


def extract_args(args):
    global config
    try:
        opts, argvs = getopt(args, 'p:m:s:n:c:d:C:D:f:g:',
            ['prefix=', 'master=', 'slaves=', 'name=', 'category-master=',
            'category-slave=', 'path=', 'date=', 'master-fields=', 'slave-fields=',
            'output='])
        for key, value in opts:
            if key == '--master-fields':
                config['master-fields'] = value.split(',')
            elif key == '--slave-fields':
                config['slave-fields'] = value.split(',')
            elif key == '--slaves':
                config['slaves'] = value.split(',')
            else:
                config[key[2:]] = value
    except (GetoptError, KeyError) as e:
        print(e)
        help()


def uniformize(master_table, slave_tables):
    new_table = CSV()
    master_fields = get_config('master-fields')
    slave_fields = get_config('slave-fields')
    new_table.addcol('epoch')
    for f in master_fields:
        new_table.addcol(f)
    for f in slave_fields:
        new_table.addcol(f)

    index = 0
    for line in master_table:
        data_line = dict(epoch=line['epoch'])
        for k in master_fields:
            data_line[k] = line[k]
        try:
            for table in slave_tables:
                for k in slave_fields:
                    if k in data_line:
                        data_line[k] += table[index][k]
                    else:
                        data_line[k] = table[index][k]
            new_table.addline(data_line)
        except IndexError:
            break
        finally:
            index += 1
    return new_table


def relativelize(table):
    first_line = deepcopy(table[0])
    for index in range(len(table)):
        for k in first_line.keys():
            table[k][index] -= first_line[k]


if __name__ == '__main__':
    extract_args(argv[1:])
    master_file = open('%s/%s/%s-%s/%s-%s' % (
        get_config('path', '.'),
        get_config('name'),
        get_config('prefix'),
        get_config('master'),
        get_config('category-master'),
        get_config('date')), 'r')
    master_table = CSV(master_file)
    slave_tables = []
    for slave in get_config('slaves'):
        slave_file = open('%s/%s/%s-%s/%s-%s' % (
            get_config('path', '.'),
            get_config('name'),
            get_config('prefix'),
            slave,
            get_config('category-slave'),
            get_config('date')), 'r')
        tbl = CSV(slave_file)
        slave_tables.append(tbl)

    aggregated = uniformize(master_table, slave_tables)
    relativelize(aggregated)

    with open(get_config('output', get_config('name')), 'w') as f:
        f.write(str(aggregated))

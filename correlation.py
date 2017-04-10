#!/usr/bin/python
from sys import argv, stderr
from getopt import getopt, GetoptError
from is_close import isclose
import math
import re
#import crash_on_ipy
cfg = dict()


def help():
    name = argv[0]
    print 'Usage: %s -x=<XColumn> -y=<YColumn> [-v/--verbose] <CSVFilePath>' % name
    print 'Note, value of specified columns shall be numeric.'


def config(key, default=None):
    if key in cfg and cfg[key]:
        return cfg[key]
    if default is not None :
        return default
    else:
        raise Exception('Missing config key %s' % key)

csv = dict()
columns = list()
x = list()
y = list()


def isdecimal(text):
    return re.match(r'^\-?\d+\.?\d*$', text)


def load_csv(fileobj):
    global csv, columns
    content = fileobj.read()
    lines = content.split('\n')
    headers = lines[0].split(',')
    for col in headers:
        if col:
            csv[col] = list()
            columns.append(col)

    for line in lines[1:]:
        cols = line.split(',')
        for i in range(len(cols)):
            if i >= len(columns):
                continue
            csv[columns[i]].append(cols[i])


def process_xy(x_col, y_col):
    global x, y, csv, columns
    j = 0
    y_val = 0
    for i in range(len(csv[x_col])):
        if i >= len(csv[y_col]):
            break
        if not isdecimal(csv[x_col][i]) or not isdecimal(csv[y_col][i]):
            continue
        if float(csv[x_col][i]) <= 0 or float(csv[y_col][i]) <= 0:
            continue
        if j > 0:
            if isclose(x[j - 1], float(csv[x_col][i])):
                if y[j-1] <= float(csv[y_col][i]):
                    y[j - 1] = float(csv[y_col][i])
                continue

        if j == 0 or y[j-1] <= float(csv[y_col][i]):
            x.append(float(csv[x_col][i]))
            y.append(float(csv[y_col][i]))
            j += 1


def compute_rel():
    x_bar = 0; y_bar = 0; n = len(x)
    cov_xy = 0
    div_x = 0; div_y = 0
    if n <= 1:
        stderr.write('\033[1;31m Insufficient samples - Cannot compute.\033[0m\n')
        exit(0)
    for i in range(n):
        x_bar += x[i] / n
        y_bar += y[i] / n
    for i in range(n):
        div_x += (x[i] - x_bar) ** 2
        div_y += (y[i] - y_bar) ** 2
        cov_xy += (x[i] - x_bar) * (y[i] - y_bar)
    div_x /= n
    div_y /= n
    cov_xy /= n

    if isclose(div_x, 0.0) or isclose(div_y, 0.0):
        stderr.write('\033[1;31m Variance is zero.\033[0m\n')
        exit(0)
    b = cov_xy / div_x
    a = y_bar - b * x_bar
    r = cov_xy / (math.sqrt(div_x) * math.sqrt(div_y))
    return b, a, r, n


def extract_args(args):
    global cfg
    try:
        opts, argvs = getopt(args, 'vx:y:', ['verbose', 'x=', 'y='])
        for key, value in opts:
            if key in ('-v', '--verbose'):
                cfg['verbose'] = True
            if key in ('-x', '--x'):
                cfg['x'] = value
            if key in ('-y', '--y'):
                cfg['y'] = value
        cfg['file'] = argvs[0]
    except GetoptError, KeyError:
        help()

if __name__ == '__main__':
    extract_args(argv[1:])
    file_path = config('file')
    f = open(file_path, 'r')
    load_csv(f)
    f.close()
    process_xy(config('x'), config('y'))
    b, a, r, n = compute_rel()
    if config('verbose', default=False):
        print 'x,\ty'
        for i in range(len(x)):
            print '%f,\t%f' % (x[i], y[i])
    print '%s,%s,%s,%d,%f,%f,%f' % (file_path, config('x'), config('y'), 
            n, b, a, r)


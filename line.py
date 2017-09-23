#!/usr/bin/python
from sys import argv
from getopt import getopt, GetoptError
import math
import pdb
cfg = dict()
csv = dict()
x = []
y1 = []
y2 = []
columns = []


def config(key, default=None):
    if key in cfg and cfg[key]:
        return cfg[key]
    if default is not None:
        return default
    else:
        raise Exception('Missing config key %s' % key)


def extract_args(args):
    global cfg
    try:
        opts, argvs = getopt(args, '', ['x=', 'y1=', 'y2=', 'xlabel=', 'y1label=', 'y2label', 'tofile'])
        for key, value in opts:
            if key == '--x':
                cfg['x'] = value
            if key == '--y1':
                cfg['y1'] = value
            if key == '--y2':
                cfg['y2'] = value
            if key == '--xlabel':
                cfg['xlabel'] = value
            if key == '--y1label':
                cfg['y1label'] = value
            if key == '--y2lable':
                cfg['y2lable'] = value
            if key == '--tofile':
                cfg['tofile'] = True
        cfg['file'] = argvs[0]
    except (GetoptError, KeyError):
        help()


def help():
    pass


def load_csv(fileobj):
    global csv, columns
    content = fileobj.read()
    lines = content.splitlines()
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


def load_xy(x_col, y1_col, y2_col):
    last_values = [0,0,0]
    for i in range(len(csv[x_col])):
        if i >= len(csv[y1_col]) or i >= len(csv[y2_col]):
            break
        if csv[x_col][i] < 0 or csv[y1_col][i] < 0 or csv[y2_col][i] < 0:
            continue
        if csv[x_col][i] < last_values[0]:
            continue
        if csv[y1_col][i] < last_values[1]:
            continue
        if csv[y2_col][i] < last_values[2]:
            continue
        x.append(float(csv[x_col][i]))
        y1.append(float(csv[y1_col][i]))
        y2.append(float(csv[y2_col][i]))
        last_values[0] = x[i]
        last_values[1] = y1[i]
        last_values[2] = y2[i]


def round_to_max(num):
    index = math.floor(math.log10(num)) if num > 0 else 0
    tenth = math.pow(10, index - 1)
    return (num // tenth + 1) * tenth * 1.1


if __name__ == '__main__':
    extract_args(argv[1:])
    file_path = config('file')
    f = open(file_path, 'r')
    load_csv(f)
    f.close()

    load_xy(config('x'), config('y1'), config('y2'))
    data_pair_1 = ''
    data_pair_2 = ''
    y1_max = 0
    y2_max = 0

    for i in range(len(x)):
        data_pair_1 += '\t\t(%f, %f)\n' % (x[i], y1[i])
        data_pair_2 += '\t\t(%f, %f)\n' % (x[i], y2[i])
        if y1[i] > y1_max:
            y1_max = y1[i]
        if y2[i] > y2_max:
            y2_max = y2[i]

    code = '\
    \\begin{tikzpicture}\n\
    \\begin{axis}[\n\
        width=7cm,\n\
        height=4.33cm,\n\
        ylabel={%s},\n\
        xlabel={%s},\n\
        ymax=%d,\n\
        axis y line*=left,\n\
        y axis style=zebrablue,\n\
    ]\n\
\n\
    \\addplot[smooth,mark=none,line width=1pt,zebrablue] coordinates {\n\
        %s\
    };\n\
    \end{axis}\n\
\n\
    \\begin{axis}[\n\
        width=7cm,\n\
        height=4.33cm,\n\
        ylabel={%s},\n\
        ymax=%d,\n\
        axis y line*=right,\n\
        axis x line*=none,\n\
        y axis style=zebrared\n\
    ]\
\n\
    \\addplot[smooth,mark=none,line width=1pt,zebrared] coordinates {\n\
        %s\
    };\n\
    \end{axis}\n\
\end{tikzpicture}\n' % (config('y1label', config('y1')).replace('_', '\\_'),
                        config('xlabel', config('x')).replace('_', '\\_'), round_to_max(y1_max), data_pair_1,
                        config('y2label', config('y2')).replace('_', '\\_'),
                        round_to_max(y2_max), data_pair_2)

    if config('tofile', False):
        filename = '%s-%s-%s-%s.tex' % (''.join(config('file').split('.')[:-1]),
                                     config('x'), config('y1'), config('y2'))
        with open(filename, 'w') as f:
            f.write(code)
    else:
        print(code)

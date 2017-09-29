#!/usr/bin/python
from sys import argv
from getopt import getopt
from correlation import load_csv, process_xy, compute_rel
from line import round_to_max
import math
import correlation
cfg = dict()


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
        opts, argvs = getopt(args, '', ['x=', 'y=', 'xlabel=', 'ylabel=', 'xunit=', 'yunit=', 'tofile'])
        for key, value in opts:
            if key == '--x':
                cfg['x'] = value
            if key == '--y':
                cfg['y'] = value
            if key == '--xlabel':
                cfg['xlabel'] = value
            if key == '--ylabel':
                cfg['ylabel'] = value
            if key == '--xunit':
                cfg['xunit'] = value
            if key == '--yunit':
                cfg['yunit'] = value
            if key == '--tofile':
                cfg['tofile'] = True
        cfg['file'] = argvs[0]
    except (GetoptError, KeyError):
        help()


def help():
    pass


if __name__ == '__main__':
    extract_args(argv[1:])
    file_path = config('file')
    f = open(file_path, 'r')
    load_csv(f)
    f.close()
    process_xy(config('x'), config('y'))
    try:
        b, a, r, n = compute_rel()
    except ArithmeticError:
        b, a, r, n = 0, 0, 0, 0

    data_pair = ''
    y_max = 0
    x_max = 0
    for i in range(len(correlation.x)):
        data_pair += '(%f, %f)\n' % (correlation.x[i],
                                     correlation.y[i])
        if correlation.y[i] > y_max:
            y_max = correlation.y[i]
        if correlation.x[i] > x_max:
            x_max = correlation.x[i]

    code = '\\begin{tikzpicture}\n\
    \\begin{axis}[\n\
        width=4cm,\n\
        height=4.33cm,\n\
        tick pos=left,\n\
        ymajorgrids=true,\n\
        ylabel={%s (%s)},\n\
        xlabel={%s},\n\
        ymax=%d,\n\
        xmajorgrids, scaled x ticks={base 10:-%d},\n\
    ]\n\
    \\addplot[zebrablue, domain=0:%d] {%f*x + %f};\n\
    \\addplot[only marks,mark=*,mark size=1pt,zebrared] coordinates {\n\
        %s\
    };\n\
    \end{axis}\n\
    \end{tikzpicture}\n' % (config('ylabel', config('y')).replace('_', '\\_'), config('yunit', 'bytes'),
                            config('xlabel', config('x')).replace('_', '\\_'), 
                            round_to_max(y_max),
                            int(math.log10(x_max)) - 1,
                            round_to_max(x_max), b, a, data_pair)

    if config('tofile', False):
        filename = '%s-%s-%s.tex' % (''.join(config('file').split('.')[:-1]),
                                     config('x'), config('y'))
        with open(filename, 'w') as f:
            f.write(code)
    else:
        print(code)

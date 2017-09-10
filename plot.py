#!/usr/bin/python
"""
%y = 1.56826e-06 x ^3 - 0.000193 x ^2 + 5.47289 x - 496.95748
%x = [20, 40, 60, 80, 100, 200, 400, 800, 1600, 3200, 6500]
%y = [0.5, 0.5, 1.0, 2.0, 4.0, 8.25, 18.5]
\begin{tikzpicture}
    \begin{axis}[
        width=7cm,
        height=4.33cm,
        tick pos=left,
        ymajorgrids=true,
        ylabel={Response Time (ms)},
        xlabel={Blocks},
        ymax=20,
        legend columns=1,
        legend cell align=left,
        legend pos=north west,
        legend style={draw=none,nodes={inner sep=2pt},nodes=right,fill=none},
    ]
    \addplot[zebrablue, domain=0:7000] {0.00282*x - 0.19359};
    \addlegendentry{Fitted curve}
    

    \addplot[only marks,mark=*,zebrared] coordinates {
        (100, 0.5)
        (200, 0.5)
        (400, 1.0)
        (800, 2.0)
        (1600, 4.0)
        (3200, 8.25)
        (6500, 18.5)
    };
    \addlegendentry{Experiments}
    \end{axis}
\end{tikzpicture}
"""
from sys import argv
from getopt import getopt
from correlation import load_csv, process_xy, compute_rel
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
        opts, argvs = getopt(args, '', ['x=', 'y=', 'xlabel=', 'ylabel=', 'tofile'])
        for key, value in opts:
            if key == '--x':
                cfg['x'] = value
            if key == '--y':
                cfg['y'] = value
            if key == '--xlabel':
                cfg['xlabel'] = value
            if key == '--ylabel':
                cfg['ylabel'] = value
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
    b, a, r, n = compute_rel()

    data_pair = ''
    y_max = 0
    for i in range(len(correlation.x)):
        data_pair += '(%f, %f)\n' % (correlation.x[i],
                                     correlation.y[i])
        if correlation.y[i] > y_max:
            y_max = correlation.y[i]

    code = '\\begin{tikzpicture}\n\
    \\begin{axis}[\n\
        width=7cm,\n\
        height=4.33cm,\n\
        tick pos=left,\n\
        ymajorgrids=true,\n\
        ylabel=%s,\n\
        xlabel={%s},\n\
        ymax=%d,\n\
        legend columns=1,\n\
        legend cell align=left,\n\
        legend pos=north west,\n\
        legend style={draw=none,nodes={inner sep=2pt},nodes=right,fill=none},\n\
    ]\n\
    \\addplot[zebrablue, domain=0:%d] {%f*x + %f};\n\
    \\addlegendentry{Fitted curve}  \n\
    \\addplot[only marks,mark=*,zebrared] coordinates {\n\
        %s\
    };\n\
    \addlegendentry{Experiments}\n\
    \end{axis}\n\
    \end{tikzpicture}\n' % (config('xlabel', config('x')),
                            config('ylabel', config('y')),
                            y_max, n, b, a, data_pair)

    if config('tofile', False):
        filename = '%s-%s-%s.tex' % (''.join(config('file').split('.')[:-1]),
                                     config('x'), config('y'))
        with open(filename, 'w') as f:
            f.write(code)
    else:
        print(code)

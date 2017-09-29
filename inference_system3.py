#!/usr/bin/env python3
from csv import CSV
from sys import argv, stderr
from is_close import isclose
from statistic import compute_rel
from tube import Tube
from getopt import getopt, GetoptError
import time

cfg = dict()


def logging(msg):
    if config('verbose', False):
        print(msg, file=stderr)


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
        opts, argvs = getopt(args, 'thv', ['mdf=', 'iof=', 'tf=', 'tubesize=', 'if=', 'fd-fm=', 'help', 'timing', 'verbose'])
        for key, value in opts:
            if key == '--mdf':
                cfg['mdf'] = value.split(',')
            if key == '--iof':
                cfg['iof'] = value.split(',')
            if key == '--tubesize':
                cfg['tubesize'] = int(value)
            if key == '--if':
                cfg['inputf'] = value
            if key == '--tf':
                cfg['timef'] = value
            if key == '--fd-fm':
                cfg['fd-fm'] = int(value)
            if key in ('--help', '-h'):
                help()
            if key in ('--timing', '-t'):
                cfg['timing'] = True
            if key in ('--verbose', '-v'):
                cfg['verbose'] = True
    except (GetoptError, KeyError):
        help()
    except ValueError:
        print('Be aware that --tubesize/--fd-fn shall be integer.')
        help()


def help():
    print ('Usage: %s --mdf=<r,w> --iof=<r,w> --tf=<time_field> --tubesize=<Tube size> --if=<Input file> --fd-fn=<f(d)/f(m)>' % argv[0])
    exit(0)


def review_time(table):
    tf = config('timef', 'time')
    last_time = 0
    interval = 50
    for i in range(len(table)):
        t = table[tf][i]
        if t > last_time:
            interval = t - last_time
            last_time = t
        if t < last_time or (t == last_time and i > 0):
            table.setcell(tf, i, last_time + interval)
            last_time += interval


if __name__ == '__main__':
    extract_args(argv[1:])
    time_field = config('timef', 'time')
    f = open(config('inputf'), 'r')
    source = CSV(f)
    review_time(source)
    f.close()
    spec = CSV()
    spec.addcol('time')
    spec.addcol('read-infer')
    spec.addcol('read')
    spec.addcol('write-infer')
    spec.addcol('write')
    src_keys = source.keys()
    samples_r = Tube(config('tubesize', 5))
    samples_w = Tube(config('tubesize', 5))
    fd_fm = config('fd-fm', 5)
    iofr, iofw = config('iof')
    mdfr, mdfw = config('mdf')
    br, ar, rr, nr = -1, 0, 0, 0  # Set b = -1 to imply unintialized specs
    bw, aw, rw, nw = -1, 0, 0, 0

    start_time = time.time()
    for i in range(len(source)):
        if i % fd_fm == 0:
            samples_r.push((
                source[mdfr][i], source[iofr][i]
            ))
            samples_w.push((
                source[mdfw][i], source[iofw][i]
            ))
            if len(samples_r) > 2:
                x_r = [samples_r[j][0] for j in range(len(samples_r))]
                y_r = [samples_r[j][1] for j in range(len(samples_r))]
                x_w = [samples_w[j][0] for j in range(len(samples_w))]
                y_w = [samples_w[j][1] for j in range(len(samples_w))]
                br, ar, rr, nr = compute_rel(x_r, y_r)
                logging('br=%.3f, rr=%.3f, nr=%.3f' % (br, rr, nr))
                bw, aw, rw, nw = compute_rel(x_w, y_w)
                logging('bw=%.3f, rw=%.3f, nw=%.3f' % (bw, rw, nw))
        r_infer = br * source[mdfr][i] + ar if br >= 0 else source[iofr][i]
        r = source[iofr][i]
        w_infer = bw * source[mdfw][i] + aw if bw >= 0 else source[iofw][i]
        w = source[iofw][i]
        spec.addline({
            'time': source[time_field][i],
            'read-infer': r_infer,
            'read': r,
            'write-infer': w_infer,
            'write': w
        })
    end_time = time.time()
    if config('timing', False):
        time_elapse = end_time - start_time
        throughput = len(source) / time_elapse
        print('Time elapsed: %.2f msec, Throughput: %.2f metrics/sec' % (time_elapse*1000, throughput))
    else:
        print(spec)

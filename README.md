# HadoopMetrics Toolkit

A Series of Tools for Hadoop Metrics analysis

# File List

## Executables

### `analyze.py` 

Extract specified metrics fields from Metrics log files in namenode and datanodes, and converts them into .csv table.

### `autoget`           

Acquire Metrics log files by tasks automatically

### `ceph_collector.py` 

Collect Ceph's perf counter data in CSV table, which can be logged with `collectd`, and extract specified fields
for master and slaves respectively

### `correlation.py`

Compute the Pearson correlation coefficient _R_ as well as coefficents of the linear regression equation
y = _b_x + _a_ of two groups of values _X_ and _Y_ which are extracted from specified CSV table.

### `everything`

A glue script that executes `analyze.py` and `correlation.py` sequentially, given Metrics data provided.

### `getdata`

Retrieve Metrics data of a period of time from the HDFS cluster.

### `inference_system1.py`

Prototype v1 - Deprecated for terrible fitting.

### `inference_system2.py`

Prototype v2

### `inference_system3.py`

Prototype v3

### `line.py`

Generate LaTex code of a line diagram consisting of three groups of data _X_, _y1_, _y2_. Generated
code is based on `pgfplots` package.

### `plot.py`

Generate LaTex code of a scatter plot consisting of two groups of data _x_ and _y_.

### `task`

Retrieve Hadoop Yarn tasks via its JMX API, presenting the task name, start time and end time.

## Classes and Libraries

### `color.py`

Functions regarding colored outputs to the UNIX terminal. Supports xterm-256color and xterm-(16)color.

### `crash_on_ipy.py`

Import this to automatically go to iPython debugging shell when error occurs.

### `csv.py`

CSV class library for higher level operations.

However currently this class could only parse CSV files whose dimension is X by Y without defects
and the first line should be header and the rest shall be numbers.

### `is_close.py`

Compare equality of two float numbers

### `statistic.py`

A function to compute linear regression related coefficients $b$, $a$, $R$.

Returns $b$, $a$, $r$, $n$, where $b$ is slope, $n$ is number of samples.

### `tube.py`

A data structure that can kick out the existing earliest pushed element if a new element is
pushed when its size has reached the set limit. Essentially it's a circular queue.

## Configuration Files

### `config.py`

### `datanode`

List of hostnames or IPs of slaves on which datanode and node managers run.

### `namenode`

List of hostname or IP of the master machine where namenode and resource manager runs.

## Others

# Requirements

Let's use Python 3.6.2 (Or later).
The earlier versions should go to the museum.

Let's throw away Python 2 anyway. They should be obsolete.

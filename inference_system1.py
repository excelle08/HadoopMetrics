import subprocess
import math

print('Please input the path of NAMENODE OUTPUT FILE(.csv) you want to infer:')
namenode_file = input()

namenode_metric_r = list()
namenode_metric_w = list()
datanode_metric_r = list()
datanode_metric_w = list()
datanode_metric_r_infer = list()
datanode_metric_w_infer = list()
count = 0
#lines_select = list()

with open(namenode_file, 'r') as f:
    lines = f.readlines()
    lines_cut = lines[:len(lines) // 3]
    #lines_cut = lines[::5]
    #for line in lines_cut:
    #    if count % 10 == 0:
    #       lines_select.append(lines_cut[count])
    #    count += 1

    for line in lines[1:]:  ###
        if line  == '\n':
            continue
        namenode_metric_r.append(line.split(',')[0])
        namenode_metric_w.append(line.split(',')[1])
        datanode_metric_r.append(float(line.split(',')[2]))
        datanode_metric_w.append(float(line.split(',')[3]))
    for line in lines_cut[1:]:
        datanode_metric_r_infer.append(float(line.split(',')[2]))
        datanode_metric_w_infer.append(float(line.split(',')[3]))

with open(namenode_file+'_new.csv', 'w') as f:
    f.writelines(lines_cut)

namenode_file_new = namenode_file+'_new.csv'

print('Calculating correlation coefficient of READ OPERATIONS...')
print('namenode metric for read operation——GetBlockLocations, datanode metric for read operation——BytesRead')
#os.system('./correlation.py -v --x=GetBlockLocations --y=BytesRead %s' %namenode_file_new)
correlation_read = subprocess.run(('./correlation.py --ignore-zero-var --x=GetBlockLocations --y=BytesRead %s' %namenode_file_new).split(' '), stdout = subprocess.PIPE)
print('Calculating correlation coefficient of WRITE OPERATIONS...')
print('namenode metric for write operation——AddBlockOps, datanode metric for write operation——BytesWritten')
#os.system('./correlation.py -v --x=AddBlockOps --y=BytesWritten %s' %namenode_file_new)
correlation_write = subprocess.run(('./correlation.py --ignore-zero-var --x=AddBlockOps --y=BytesWritten %s' %namenode_file_new).split(' '), stdout = subprocess.PIPE)

#print(correlation_read.stdout, correlation_write.stdout)
read_args = correlation_read.stdout.decode('utf-8').split(',')
write_args = correlation_write.stdout.decode('utf-8').split(',')
#   y = b * x + a
#   a_read,b_read,a_write,b_write needed
a_read = float(read_args[5])
b_read = float(read_args[4])
a_write = float(write_args[5])
b_write = float(write_args[4])

for i in range(len(namenode_metric_r)//3, len(namenode_metric_r)):
    datanode_metric_r_infer.append(b_read * float(namenode_metric_r[i]) + a_read)
    datanode_metric_w_infer.append(b_write * float(namenode_metric_w[i]) + a_write)
'''
print('Compare our INFERENCE list of datanode read metric(above) and the ACTUAL one(below):')
print(datanode_metric_r_infer)
print(datanode_metric_r)
print('Compare our INFERENCE list of datanode write metric(above) and the ACTUAL one(below):')
print(datanode_metric_w_infer)
print(datanode_metric_w)
'''

print ('BytesRead_Infer,BytesRead,BytesWritten_Infer,BytesWritten')
for i in range(len(datanode_metric_r)):
    print (datanode_metric_r_infer[i],',',datanode_metric_r[i],',',datanode_metric_w_infer[i],',',datanode_metric_w[i])


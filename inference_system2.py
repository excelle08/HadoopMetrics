import math
from sys import stderr
from is_close import isclose


print('Please input the path of NAMENODE OUTPUT FILE(.csv) you want to infer:')
namenode_file = input()

namenode_metric_r = list()
namenode_metric_w = list()
datanode_metric_r = list()
datanode_metric_w = list()
datanode_metric_r_infer = list()
datanode_metric_w_infer = list()



with open(namenode_file, 'r') as f:
    lines = f.readlines()
    #lines_cut = lines[:len(lines) // 2]
    lines_before = lines[1:]
    lines_cut = lines_before[::5]

    ###append actual data to separate list###
    for line in lines[1:]:
        if line  == '\n':
            continue

        namenode_metric_r.append(float(line.split(',')[0]))
        namenode_metric_w.append(float(line.split(',')[1]))
        datanode_metric_r.append(float(line.split(',')[2]))
        datanode_metric_w.append(float(line.split(',')[3]))

#with open(namenode_file+'_new.csv', 'w') as f:
 #   f.writelines(lines_cut)

'''
namenode_file_new = namenode_file+'_new.csv'

print('Calculating correlation coefficient of READ OPERATIONS...')
print('namenode metric for read operation——GetBlockLocations, datanode metric for read operation——BytesRead')
#os.system('./correlation.py -v --x=GetBlockLocations --y=BytesRead %s' %namenode_file_new)
correlation_read = subprocess.run(('./correlation.py --x=GetBlockLocations --y=BytesRead %s' %namenode_file_new).split(' '), stdout = subprocess.PIPE)
print('Calculating correlation coefficient of WRITE OPERATIONS...')
print('namenode metric for write operation——AddBlockOps, datanode metric for write operation——BytesWritten')
#os.system('./correlation.py -v --x=AddBlockOps --y=BytesWritten %s' %namenode_file_new)
correlation_write = subprocess.run(('./correlation.py --x=AddBlockOps --y=BytesWritten %s' %namenode_file_new).split(' '), stdout = subprocess.PIPE)

'''

x_read = list()
y_read = list()
x_write = list()
y_write = list()

for line in lines_cut:
    if line == '\n':
        continue
    x_read.append(float(line.split(',')[0]))
    y_read.append(float(line.split(',')[2]))
    x_write.append(float(line.split(',')[1]))
    y_write.append(float(line.split(',')[3]))

def compute_rel(x,y):
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
        #stderr.write('\033[1;31m Variance is zero.\033[0m\n')
        return 0, y[0], 1, 2
    b = cov_xy / div_x
    a = y_bar - b * x_bar
    r = cov_xy / (math.sqrt(div_x) * math.sqrt(div_y))
    return b, a, r, n


barn_r = list()
barn_w = list()
datanode_metric_r_infer = datanode_metric_r[:6]
datanode_metric_w_infer = datanode_metric_w[:6]
#b = barn[0], a = barn[1], r = barn[2], n = barn[3]

for i in range(2, len(x_read)):
    barn_r = compute_rel(x_read[:i],y_read[:i])
    if len(datanode_metric_r_infer) < len(datanode_metric_r):
        datanode_metric_r_infer.append(barn_r[0] * namenode_metric_r[5 * i - 4] + barn_r[1])
    if len(datanode_metric_r_infer) < len(datanode_metric_r):
        datanode_metric_r_infer.append(barn_r[0] * namenode_metric_r[5 * i - 3] + barn_r[1])
    if len(datanode_metric_r_infer) < len(datanode_metric_r):
        datanode_metric_r_infer.append(barn_r[0] * namenode_metric_r[5 * i - 2] + barn_r[1])
    if len(datanode_metric_r_infer) < len(datanode_metric_r):
        datanode_metric_r_infer.append(barn_r[0] * namenode_metric_r[5 * i - 1] + barn_r[1])
    if len(datanode_metric_r_infer) < len(datanode_metric_r):
       # datanode_metric_r_infer.append(datanode_metric_r[5 * i])
       datanode_metric_r_infer.append(barn_r[0] * namenode_metric_r[5 * i - 1] + barn_r[1])

for j in range(2, len(x_write)):
    barn_w = compute_rel(x_write[:j],y_write[:j])
    if len(datanode_metric_w_infer) < len(datanode_metric_w):
        datanode_metric_w_infer.append(barn_w[0] * namenode_metric_w[5 * i - 4] + barn_w[1])
    if len(datanode_metric_w_infer) < len(datanode_metric_w):
        datanode_metric_w_infer.append(barn_w[0] * namenode_metric_w[5 * i - 3] + barn_w[1])
    if len(datanode_metric_w_infer) < len(datanode_metric_w):
        datanode_metric_w_infer.append(barn_w[0] * namenode_metric_w[5 * i - 2] + barn_w[1])
    if len(datanode_metric_w_infer) < len(datanode_metric_w):
        datanode_metric_w_infer.append(barn_w[0] * namenode_metric_w[5 * i - 1] + barn_w[1])
    if len(datanode_metric_w_infer) < len(datanode_metric_w):
        #datanode_metric_w_infer.append(datanode_metric_w[5 * i])
        datanode_metric_w_infer.append(barn_w[0] * namenode_metric_w[5 * i - 1] + barn_w[1])
'''print('Compare our INFERENCE list of datanode read metric(above) and the ACTUAL one(below):')
print(datanode_metric_r_infer)   #BytesRead_infer
print(datanode_metric_r)           #BytesRead
print('Compare our INFERENCE list of datanode write metric(above) and the ACTUAL one(below):')
print(datanode_metric_w_infer)      #BytesWritten_infer
print(datanode_metric_w)            #BytesWritten
'''

csv = ''
fields = ['BytesRead_infer','BytesRead','BytesWritten_infer','BytesWritten']
for field in fields:
    csv += '%s,'%field
csv += '\n'

for i in range(len(datanode_metric_r_infer)):
    csv += '%s,'%datanode_metric_r_infer[i]
    csv += '%s,' % datanode_metric_r[i]
    csv += '%s,' % datanode_metric_w_infer[i]
    csv += '%s,' % datanode_metric_w[i]
    csv += '\n'

print(csv)
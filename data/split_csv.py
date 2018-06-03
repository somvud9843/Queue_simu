import csv
from os import listdir 
import glob

def init_output_file(filename):
    with open(filename, 'w', newline='') as f: 
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(["time", "DRFQ", "PR", "WRR"])

def read_csv(filename):
    new_row = []
    i = -1
    with open(filename,'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            if row[0].startswith('0'):
                new_row.append([])
                i += 1
            if i == 0:
                new_row[i].append(row)
            else:
                s = row[0].split(',')
                new_row[i].append(s[1])
    return new_row

def write_csv(filename, data):
    with open(filename, 'a', newline='') as f: 
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        min_time = min(map(len,data))
        for i in range(min_time):
            new_data = []
            for row in data:
                # print(row[i])
                if isinstance(row[i], list):
                    s = row[i][0].split(",")
                    new_data = s.copy()
                else:
                    if row[i]== "{}" :
                        row[i] = '0'
                    new_data.append(row[i])
            w.writerow(new_data)       
        avg = ["Avg"]
        for i in range(1,len(new_data),1):
            avg.append(float(new_data[i])/(min_time-1))
        w.writerow(avg)
        # w.writerow([data.f_id, data.p_num, data.size, data.time, data.VST, data.VFT])


s = glob.glob("data/*DRFQ*")
for filename in s:
    print("Read file: %s...." % filename)
    data = read_csv(filename)
    new_filename = "data/throughput" + filename[7:]
    print("Output file: %s..." % new_filename)
    init_output_file(new_filename)
    write_csv(new_filename,data)


'''
for i in s:
    filename = s[5:]
    data = read_csv(filename)
    new_filename = "throughput" + filename[1][12:]
    write_csv(new_filename,data)
'''





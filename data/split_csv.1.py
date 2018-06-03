import csv
from os import listdir 
import glob
import operator

def init_result():
    global PR_share
    PR_share = {}
    with open('result.csv','r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            s = row[0].split(",")
            key = (int(s[0]), int(s[1]), int(s[2]), int(s[3]))
            PR_share[key] = float(s[19])
        

def init_output_file(filename):
    with open(filename, 'w', newline='') as f: 
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(["time", "DRFQ", "PR", "WRR"])

def read_csv(filename):
    data = {}
    per_row = []
    with open(filename,'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        start = filename.index("(")
        end = filename.index(")")
        rp = filename[start+1:end]
        rp = map(int, rp.split(","))
        key = tuple(rp)
        for row in spamreader:
            if row[0].startswith('Avg'):
                data[key] = per_row
            per_row = row
    return data

def write_csv(filename, data):
    with open(filename, 'a', newline='') as f: 
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        for i in data:
            w.writerow(i)

def getMaxCheat(rp_unformal):
    import sys
    sys.path.append("C:/Users/YEN-WEN WANG/workspace/Queue_simu")
    import ffmodel
    rp = [
            [rp_unformal[0], rp_unformal[1]],
            [rp_unformal[2], rp_unformal[3]]
        ]
    
    result = []
    cheatA = {}
    cheatB = {}
    # Flow A cheating
    if rp[0][0] > rp[0][1]:
        for i in range(1,rp[0][0],1):
            rp_temp = [
                [rp[0][0], i],
                [rp[1][0], rp[1][1]]
            ]
            share = ffmodel.main(rp_temp)
            key = (rp_temp[0][0], rp_temp[0][1], rp_temp[1][0], rp_temp[1][1])
            cheatA[key] = share[0]/share[1]
    else:
        for i in range(1,rp[0][1],1):
            rp_temp = [
                [i, rp[0][1]],
                [rp[1][0], rp[1][1]]
            ]
            share = ffmodel.main(rp_temp)
            key = (rp_temp[0][0], rp_temp[0][1], rp_temp[1][0], rp_temp[1][1])
            cheatA[key] = share[0]/share[1]
    # Flow B cheating
    if rp[1][0] > rp[1][1]:
        for i in range(1,rp[1][0],1):
            rp_temp = [
                [rp[0][0], rp[0][1]],
                [rp[1][0], i]
            ]
            share = ffmodel.main(rp_temp)
            key = (rp_temp[0][0], rp_temp[0][1], rp_temp[1][0], rp_temp[1][1])
            cheatB[key] = share[0]/share[1]
    else:
        for i in range(1,rp[1][1],1):
            rp_temp = [
                [rp[0][0], rp[0][1]],
                [i, rp[1][1]]
            ]
            share = ffmodel.main(rp_temp)
            key = (rp_temp[0][0], rp_temp[0][1], rp_temp[1][0], rp_temp[1][1])
            cheatB[key] = share[0]/share[1]
    keyA = max(cheatA.items(), key=operator.itemgetter(1))[0]
    keyB = min(cheatB.items(), key=operator.itemgetter(1))[0]
    result = [keyA[0], keyA[1], keyA[2], keyA[3], cheatA[keyA],
              keyB[0], keyB[1], keyB[2], keyB[3], cheatB[keyB]  ]
    # print(result)
    # ex:[1, 13, 2, 11, 0.8467220683287165, 10, 13, 1, 11, 0.8450184501845018]
    return result

def main():
    s = glob.glob("data/*throughput*")
    data_set = {}
    result = []
    for filename in s:
        print("Read file: %s...." % filename)
        data = read_csv(filename)
        data_set.update(data)
        start = filename.index("(")
        end = filename.index(")")
        temp = filename[start+1:end]
        temp = map(int, temp.split(","))
        rp = list(temp)
        key = tuple(rp)
        temp = map(int, data[key][0].split(","))
        packet = list(temp)
        drpA = max(rp[0], rp[1])
        drpB = max(rp[2], rp[3])
        total = drpA + drpB
        DRFQA = packet[1] * (drpB/total)
        DRFQB = packet[1] * (drpA/total)
        PRA = packet[2] * PR_share[key]/(PR_share[key]+1)
        PRB = packet[2] * 1/(PR_share[key]+1)
        WRRA = packet[3] * PR_share[key]/(PR_share[key]+1)
        WRRB = packet[3] * 1/(PR_share[key]+1)
        cheat = getMaxCheat(rp)
        cheatAA = packet[2] * cheat[4]/(cheat[4]+1)
        cheatAB = packet[2] * 1/(cheat[4]+1)
        cheatBA = packet[2] * cheat[9]/(cheat[9]+1)
        cheatBB = packet[2] * 1/(cheat[9]+1)
        new_data = [rp[0], rp[1], rp[2], rp[3], packet[0], DRFQA, DRFQB, PRA, PRB, WRRA, WRRB,
                    cheatAA, cheatAB, cheatBA, cheatBB]
        new_data = [int(i) for i in new_data]
        new_data = new_data + cheat[:4] + cheat[5:9]
        print(new_data)
        result.append(new_data)
    write_csv('th_compare', result)
    return data
    
init_result()
main()



# key = (4,21,25,10)
# print(data[key])
# print("Flow 1 : %f , Flow 2 : %f" % (PR_share[key]/(PR_share[key]+1), 1/(PR_share[key]+1)))

from queue import Queue
from queue import PriorityQueue
import time
from operator import attrgetter
from fractions import Fraction
import sys
import random
from threading import Thread
from threading import Timer, Thread, Event
import csv
import logging
import collections



def init_output_file(fliename, head):
    with open(fliename, 'w', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(head)

def save_to_csv(fliename, data):
    with open(fliename, 'a', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(data)


class fifo_q(PriorityQueue):
    def __init__(self):
        PriorityQueue.__init__(self)
        self.counter = 0

    def put(self,priority, item):
        PriorityQueue.put(self, (priority, self.counter, item))
        self.counter += 1

    def get(self, *args, **kwargs):
        _, _, item = PriorityQueue.get(self, *args, **kwargs)
        return item

class Packet:

    def __init__(self, flow_id, p_num, size, g_time, isLast):
        self.flow_id = flow_id
        self.p_num = p_num
        self.size = size
        self.arr_time = g_time
        self.isLast = isLast

    def __lt__(self, other):
        return self.arr_time < other.arr_time


def q_go():
    t = 0
    seq = {}
    global qDict
    qDict={}
    
    while t<1*10**5:
        id = random.randint(1,len(rp))
        if not id in seq:
            seq[id] = 0
        else: 
            seq[id] += 1

        p = Packet(id, seq[id], 123, time.time(), False)
        if not id in qDict:
            qDict[id] = fifo_q()
        setRP(p, id)
        
        qDict[id].put(p.arr_time, p)
        t += 1

class Resource():
    def __init__(self, id, inputQueue, outputQueue):
        self.id = id
        self.inputQueue= inputQueue
        self.outputQueue = outputQueue
        self.packet = {}

    def process(self, remain, usage):
  
        for keys in self.inputQueue:
            if not keys in self.outputQueue:
                self.outputQueue[keys] = Queue()
            if self.outputQueue[keys].qsize()<10 :
                # print(keys, buf[keys].qsize())
                if not keys in remain.keys():
                    if not self.inputQueue[keys].empty():
                        self.packet[keys] = self.inputQueue[keys].get()
                        remain[keys] = float(self.packet[keys].rp[self.id-1])
                        logging.debug("R%d-Set id: %d-%d, size: %d at %d" % (self.id, keys, self.packet[keys].p_num, remain[keys],t-1))

        if len(remain) > 0:
            f_num = len(remain)
            r = 1 / f_num
            for f_id in list(remain.keys()):
                remain[f_id] = remain[f_id] - r
                if not (f_id in usage):
                    usage[f_id]= [r]
                else:
                    if len(usage[f_id]) < self.id:
                        usage[f_id].append(r)
                    else:
                        usage[f_id][self.id-1] = usage[f_id][self.id-1] + r

                if remain[f_id] <= 0 :
                    if f_id in self.packet:
                        logging.debug("R%d-Done id: %d-%d, at %d" % (self.id, f_id, self.packet[f_id].p_num, t))
                        self.outputQueue[f_id].put(self.packet[f_id])
                        del remain[f_id]
                    
        return remain, usage



def setRP(packet, id):
    setattr(packet, "rp", rp[id-1])
    return packet

class ffmodel(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop_event = Event()

    def run(self):
        global p_counter
        global t 
        p_counter = []
        usage = {}
        t = 1
        buf = {}
        counter = [0] * len(rp)
        remainList = [{}]
        resourceList = []
        #  init the First resource
        inputQueueList = [qDict]
        outputQueueList = [buf]
        resourceList.append(Resource(1, inputQueueList[0], outputQueueList[0]))
        for i in range(2, num_resource, 1):
            remainList.append({})
            outputQueueList.append({})
            resourceList.append(Resource(i, outputQueueList[i-2], outputQueueList[i-1]))
        remainList.append({}) # The last Resource's remain

        while sum(counter)<totalPacket:

            for i in range(0, len(resourceList), 1):
                remainList[i], usage = resourceList[i].process(remainList[i], usage)
                t += 1

            for keys in outputQueueList[num_resource-2]:
                if not outputQueueList[num_resource-2][keys].empty():
                    if not keys in remainList[num_resource-1]:
                        buf_packet = outputQueueList[num_resource-2][keys].get()
                        remainList[num_resource-1][keys] = float(buf_packet.rp[num_resource-1])
                        logging.debug("R%d-Set id: %d-%d, size: %d at %d" % (num_resource, keys, buf_packet.p_num, remainList[num_resource-1][keys], t))

            if len(remainList[num_resource-1]) > 0:
                f_num2 = len(remainList[num_resource-1])
                r = 1 / f_num2
                
                for f_id in list(remainList[num_resource-1].keys()):
                    remainList[num_resource-1][f_id] = remainList[num_resource-1][f_id] - r
                    if len(usage[f_id]) < num_resource :
                        usage[f_id].append(r)
                    else:
                        usage[f_id][num_resource-1] = usage[f_id][num_resource-1] + r
                        
                    if remainList[num_resource-1][f_id] <= 0 :
                        logging.debug("R%d-Done id: %d-%d, at %d" % (num_resource, f_id, buf_packet.p_num, t))
                        
                        counter[f_id-1] += 1
                        del remainList[num_resource-1][f_id]
                        
            t -= num_resource-2
            sys.stdout.flush()

        for key in sorted(usage.keys()):
            for resource in usage[key]:
                logging.debug( "Flow %d R%d_share: %d" % (key, usage[key].index(resource), resource))         
                # logging.debug( "R1_share: %d = %d" % (key, usage[key][0]))
                # logging.debug( "R2_share: %d = %d" % (key, usage[key][1]))
                
        
        self.output(usage, counter)
        p_counter = counter
        sys.stdout.flush()
        
        # save_to_csv(result)

    def output(self, d, c):
        total = [0] * len(d[1])
        for i in range(0, len(d[1]), 1):
            for keys in d:
                total[i] += d[keys][i]
        for keys in sorted(d.keys()):
            out_str = "Flow %d : <" % keys
            for i in range(0, len(d[keys]), 1):
                out_str += "%.3f, " % (d[keys][i]/total[i])
            out_str = out_str[:-2] + ">"
            logging.info(out_str)
        pkt = "packet Thoughput"
        for pkt_num in c:
            pkt += " "+ str(pkt_num)+":"
        logging.warning(pkt[:-1])

def main(argv):
    global rp
    global num_resource
    global totalPacket
    totalPacket = 5000
    rp = argv
    num_resource = len(rp[0])
    print(rp)
    t = Thread(target=q_go)
    t.start()
    time.sleep(0.1)
    t1 = ffmodel()
    t1.start()
    t.join()
    t1.join()
    return p_counter


def afterCheating(data):
    maxIndex = data.index(max(data))
    r = list(range(0,len(data)))
    r.remove(maxIndex)
    howmany = random.randint(1, len(data)-1)

    for i in range(0, howmany, 1):
        change_index = random.choice(r)
        r.remove(change_index)
        temp = list(range(1, data[change_index])) + list(range(data[change_index]+1, data[maxIndex]))
        data[change_index] = random.choice(temp)
    return data

def generateRP(totalNumber, resourceNumber = 2):
    data = []
    for i in range(totalNumber):
        temp = []
        for j in range(resourceNumber):
            temp.append(random.randint(1,30))
        data.append(temp)
    return data

def testFixRatioCheat():
    r = []
    cheatProfit = []
    totoalFlowNumber = 2
    totalResourceNumber = 2
    cheatRatio = 0.5
    # header = ["Number of flows", "cheat", "cheated"]
    # init_output_file("cheatProfit(50%).csv", header) 
    rp_init = [
        [16,15],
        [5,1]
    ]
    while(1):
        # 50% of flows will cheat, find how much cheat flows can get, and cheated can get
        for flow_num in range(2, totoalFlowNumber+1, 1):    
            # rp_init = generateRP(flow_num, totalResourceNumber)
            for i in range(2):
                if not i % 2 == 0:
                    for j in range(int(flow_num * cheatRatio)):
                        try:
                            rp_init[j] = afterCheating(rp_init[j])
                        except:
                            print("Error:" ,sys.exc_info()[0])
                            print("Set:", rp_init[j])
                            
                r.append(main(rp_init))

        for i in range(0, len(r), 2):
            temp = []
            for j in range(0, len(r[i]), 1):
                temp.append((r[i+1][j] - r[i][j]) / r[i][j])
            cheatProfit.append(temp)

        for i in cheatProfit:
            cheatNum = int(len(i)/2)
            cheat = sum(i[:cheatNum]) / cheatNum
            cheated = sum(i[len(i)-cheatNum:]) / (len(i)-cheatNum)
            data = [len(i), cheat, cheated]
            print(data)
            # save_to_csv("cheatProfit(50%).csv",data)
        break
        r = []
        cheatProfit = []

if __name__ == "__main__":

    FORMAT = " %(message)s"
    logging.basicConfig(level = logging.INFO,format=FORMAT)
    testFixRatioCheat()
else:
    logging.propagate = False
   
    #    print("Flow num: %d, cheat: %.3f, cheated: %.3f" % (len(i), cheat, cheated))

    # for cheatRatio in range(1, 10, 1):    
    #     for i in range(2):
    #         if not i % 2 == 0:
    #             for j in range(int(totoalFlowNumber * cheatRatio/10)):
    #                 rp_init[j] = afterCheating(rp_init[j])
    #         r.append(main(rp_init))
    

    # for i in range(0, len(r), 2):
    #     temp = []
    #     for j in range(0, len(r[i]), 1):
    #         temp.append((r[i+1][j] - r[i][j]) / r[i][j])
    #     cheatProfit.append(temp)
    # print(cheatProfit)

    # print(r)    
    
    # avgCheat = []
    # cheatRatio = 0.1
    # for v in cheatProfit:
    #     avg = sum(v[:int(len(v)*cheatRatio)]) / int(len(v)*cheatRatio)
    #     avgCheat.append(avg)
    #     cheatRatio += 0.1
    # print(avgCheat, cheatRatio)

    # rp = [
    #     [1, 8, 3],
    #     [1, 1, 5],
    #     [9, 1, 7]
    # ]
    
    

    pass

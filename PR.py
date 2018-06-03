from queue import Queue
from queue import PriorityQueue
from operator import add
from threading import Thread
import sys
import time
import random
import threading
import csv
from operator import attrgetter
import os
import logging

clear = lambda: os.system('cls')
clear()
FORMAT = " %(message)s"
logging.basicConfig(level = logging.INFO,format=FORMAT)

def save_to_csv(data):
    with open(filename, 'a', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        # w.writerow([data.f_id, data.p_num, data.size, data.time, data.VST, data.VFT])
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
        self.f_id = flow_id
        self.p_num = p_num
        self.size = size
        self.time = g_time
        self.isLast = isLast
# A thread that produces data

# Queue with resource profile

class Flow_one(Thread):

    def __init__(self,q, f_id, bw, size, resource_profile, weight):
        Thread.__init__(self)
        self.que = q
        self.id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = random.randint(10, 50)*8
        self.rp = resource_profile
        self.stopRequest = threading.Event()
        self.tout = 0
        self.alive = True
        self.weight = weight

    def run(self):
        p_seq = 0
        while on:
        # while self.alive:
            if self.tout > 0:
                self.sleep()

            # Produce some data
            time.sleep(self.p_size / self.bw) # transmission delay
            # time.sleep(0.1)
            data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, False)
            setattr(data, "rp", self.rp)
            setattr(data, "weight", self.weight)
            p_seq += 1
            self.que.put(data.time, data)
            
        data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, True)
        setattr(data, "rp", self.rp)
        setattr(data, "weight", self.weight)
        self.que.put(data.time, data)

    def sleep(self):
        print("Flow %d stop sending for %d seconds" % (self.id, self.tout))
        time.sleep(self.tout)
        self.tout = 0

    def stop(self):
        self.alive = False
        self.join()


class Classifier(Thread):
    def __init__(self, que):
        Thread.__init__(self)
        self.q = que
        self.alive = True

    def run(self):
        global sys_VT
        global actFL
        actFL={}
        while on:
            data = self.q.get()
            # classify pakcet and update ActiveFlowList
            if not(data.f_id in actFL):
                temp_q = Queue()
                actFL[data.f_id] = temp_q
                setattr(actFL[data.f_id],"pVFT", 0)
            setattr(temp_q,"f_id", data.f_id)
            setattr(data,"VST", max(sys_VT, actFL[data.f_id].pVFT))
            setattr(data,"VFT", data.VST + (data.rp[0]/data.weight))
            actFL[data.f_id].pVFT = data.VFT
            actFL[data.f_id].put(data)
            # save_to_csv(data)
            sys.stdout.flush()
    def stop(self):
        self.alive = False
        self.join()

class Scheduler(Thread):
    def __init__(self, inQueue, outQueue):
        Thread.__init__(self)
        self.inputQueue = inQueue
        self.outputQueue = outQueue

    def run(self):
        while on:
            if self.outputQueue.qsize() > 0:
                continue
            data = []
            for keys in self.inputQueue:
                if not self.inputQueue[keys].empty():
                    data.append(list(self.inputQueue[keys].queue)[0])
            data = sorted(data, key=attrgetter("f_id"))
            try:
                minVST_packet = min(data, key=attrgetter("VST"))
            except ValueError:
                continue
            except:
                logging.error("Unexpected error:" +  sys.exc_info()[0])
                break

            next_packet = actFL[minVST_packet.f_id].get()  

            
            # logging.debug("Min VST packet:%d-%d" % (next_packet.f_id,next_packet.p_num))
            self.outputQueue.put(next_packet)      

class Resource(Thread):
    def __init__(self, id, inQueue, outQueue):
        Thread.__init__(self)
        self.id = id
        self.inputQueue = inQueue
        self.outputQueue = outQueue
        self.isLast = (id == num_resource)
    def run(self):
        if self.id == 1:
            global sys_VT
        if self.id == num_resource:
            global packet_counter
            global on
            usage = {}
            packet_counter = {}
            moniter = MonitorThread()
            moniter.start()
        while on:
            packet = self.inputQueue.get()
            logging.debug("R%d Produce packet:%d-%d" % (self.id, packet.f_id, packet.p_num))
            if self.id == 1:
                logging.debug("Update System Virtual Time: %d -> %d" % (sys_VT, packet.VST))
                sys_VT = packet.VST
            time.sleep(packet.rp[0] * speed)
            self.outputQueue.put(packet)
            if self.isLast:
                if not(packet.f_id in usage):
                    usage[packet.f_id] = packet.rp
                else:
                    usage[packet.f_id] = list(map(add, usage[packet.f_id], packet.rp))
                if not packet.f_id in packet_counter:
                    packet_counter[packet.f_id] = 1
                else:
                    packet_counter[packet.f_id] += 1
                if sum(packet_counter.values()) > endPoint:
                    on = False
                    logging.info("Simulation Time: %.3f" % (time.time()-start_time))
        if self.isLast:
            self.output(usage, packet_counter)
                    
    def output(self, d, c):
        total = [0] * len(d[1])
        logging.info(d)
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
        for keys in sorted(c.keys()):
            pkt += " "+ str(c[keys])+":"
        logging.info(pkt[:-1])


class MonitorThread(Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        i = 0
        while on:
            print(i, packet_counter)
            # save_to_csv([i,packet_counter])
            i += 1
            time.sleep(1)

def main(rp, weight):
    global usage
    global speed
    global start_time
    global sys_VT
    global on
    global filename
    global num_resource
    global endPoint
    endPoint = 150
    filename = "data/666th_DRFQ(%s,%s,%s,%s).csv" % (rp[0][0],rp[0][1],rp[1][0],rp[1][1])
    speed = 10 ** -4
    usage = {}
    on = True
    num_resource = len(rp[0])
    # Create the shared queue and launch both threads
    start_time = time.time()
    
    sys_VT = 0
    # init_output_file()
    q = fifo_q()
    tList=[]
    r2Buf = {}
    f_num = len(rp)
    for i in range(1, f_num+1):
        t = Flow_one(q, i, 200*2**20, 400, rp[i-1], weight)
        t.start()
        tList.append(t)

   
    classifier = Classifier(q)
    classifier.start()
    scheduler = Scheduler(actFL, r2Buf)
    scheduler.start()
    tList.append(classifier)
    tList.append(scheduler)

    inputQueueList = [r2Buf]
    resourceList = []
    
    for i in range(1, num_resource+1, 1):
        inputQueueList.append(Queue())
        resourceList.append(Resource(i, inputQueueList[i-1], inputQueueList[i]))
        resourceList[i-1].start()
        logging.debug("Resource %d satrt." % i)
    
    tList += resourceList
    for t in tList:
        t.join()


if __name__ == "__main__":
    rp = [
        [26, 4],
        [3, 4]
    ]
    weight = 1
    main(rp , weight)


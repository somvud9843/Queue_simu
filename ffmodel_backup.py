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


FORMAT = " %(message)s"
logging.basicConfig(level = logging.INFO,format=FORMAT)


def init_output_file():
    with open('test.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        # w.writerow(["f_id", "p_num", "size", "time", "VST", "VFT"])

def save_to_csv(data):
    with open('simu.csv', 'a', newline='') as f:  # Just use 'w' mode in 3.x
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
        id = random.randint(1,2)
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


def setRP(packet, id):
    # rp = [
    #   [15, 17], [6, 1]
    # ]
    setattr(packet, "rp", rp[id-1])
    return packet


# def slove_funtion():
#     x = Symbol('x')
#     y = Symbol('y')
#     f=Fraction(4, 2)
#     f1 = 20 * x + 20 * y - 1
#     f2 = 1 * x + 1 * y - 1
#     sol = solve((f1, f2), x, y)
#     print(sol)
#     # OUT: {x: 50, y: 30, z: 20}


def ffmodel_(qDict):
    remain = {}
    remain2 = {}
    packet = {}
    usage = {}
    t = 1 
    buf  = dict.fromkeys(qDict)

    while t<28*10**3:
        for keys in qDict:
            if buf[keys] == None:
                if not keys in remain.keys():
                    if not qDict[keys].empty():
                        packet[keys] = qDict[keys].get()
                        remain[keys] = float(packet[keys].rp[0])
                        # print("Set id: %d , size: %d" % (keys, remain[keys]))
        if len(remain) > 0:
            f_num = len(remain)
            r = 1 / f_num
            
            for f_id in list(remain.keys()):
                remain[f_id] = remain[f_id] - r
                if not (f_id in usage):
                    usage[f_id]= [r]
                else:
                    usage[f_id][0] = usage[f_id][0] + r

                if remain[f_id] == 0 :
                    # print("R1----------packet %d Done at %d." % (f_id, t ))
                    buf[f_id] = packet[f_id]
                    del remain[f_id]
                    
        for keys in buf:
            if buf[keys] != None:
                if not keys in remain2.keys():
                    remain2[keys] = float(buf[keys].rp[1])
                    buf[keys] = None
                    # print("R2----------Set id: %d , size: %d" % (keys, remain2[keys]))
        print(t)
        t += 1

        if len(remain2) > 0:
            f_num2 = len(remain2)
            r2 = 1 / f_num2
            
            for f_id in list(remain2.keys()):
                remain2[f_id] = remain2[f_id] - r2
                if len(usage[f_id]) <= 2 :
                    usage[f_id].append(r)
                else:
                    usage[f_id][1] = usage[f_id][1] + r
                    
                if remain2[f_id] == 0 :
                    # print("R2************packet %d Done at %d." % (f_id, t ))
                    del remain2[f_id]
        
        sys.stdout.flush()
    for key in usage:
            print("--"*50, "R1_share: %d = %d" % (key, usage[key][0]))
            print("--"*50, "R2_share: %d = %d" % (key, usage[key][1]))


class ffmodel(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop_event = Event()

    def run(self):
        global p_counter
        p_counter = []
        remain = {}
        remain2 = {}
        packet = {}
        usage = {}
        t = 1
        # buf  = dict.fromkeys(self.q)
        buf = {}
        counter_f1 = 0
        counter_f2 = 0
        start={}
        end={}
        # print(qDict[1].get().__dict__)
        # while t<2*10**4:
        while counter_f1+counter_f2<10000:
            for keys in qDict:
                if not keys in buf:
                    buf[keys] = Queue()
                if buf[keys].qsize()<10 :
                    # print(keys, buf[keys].qsize())
                    if not keys in remain.keys():
                        if not qDict[keys].empty():
                            packet[keys] = qDict[keys].get()
                            remain[keys] = float(packet[keys].rp[0])
                            logging.debug("R1-Set id: %d-%d, size: %d at %d" % (keys, packet[keys].p_num, remain[keys],t-1))

                            if not (keys,1) in start.keys(): 
                                start[keys,1] = [t-1]    
                            else:
                                start[keys,1].append(t-1)


            if len(remain) > 0:
                f_num = len(remain)
                r = 1 / f_num
                for f_id in list(remain.keys()):
                    remain[f_id] = remain[f_id] - r
                    if not (f_id in usage):
                        usage[f_id]= [r]
                    else:
                        usage[f_id][0] = usage[f_id][0] + r

                    if remain[f_id] == 0 :
                        logging.debug("R1-Done id: %d-%d, at %d" % (f_id, packet[f_id].p_num, t))
                        buf[f_id].put(packet[f_id])

                        if not (f_id,1) in end.keys(): 
                            end[f_id,1] = [t]    
                        else:
                            end[f_id,1].append(t)

                        del remain[f_id]
                        
            for keys in buf:
                if not buf[keys].empty():
                    if not keys in remain2.keys():
                        buf_packet = buf[keys].get()
                        remain2[keys] = float(buf_packet.rp[1])
                        # logging.debug("R2-Set id: %d-%d, size: %d at %d" % (keys,buf_packet.p_num, remain2[keys], t))

                        if not (keys,2) in start.keys(): 
                            start[keys,2] = [t]    
                        else:
                            start[keys,2].append(t)

                        # buf[keys] = None
                        
                        
            t += 1

            if len(remain2) > 0:
                f_num2 = len(remain2)
                r2 = 1 / f_num2
                
                for f_id in list(remain2.keys()):
                    remain2[f_id] = remain2[f_id] - r2
                    if len(usage[f_id]) <= 2 :
                        usage[f_id].append(r2)
                    else:
                        usage[f_id][1] = usage[f_id][1] + r2
                        
                    if remain2[f_id] == 0 :
                        # logging.debug("R2-Done id: %d, at %d" % (keys, t))

                        if not (f_id,2) in end.keys(): 
                            end[f_id,2] = [t]    
                        else:
                            end[f_id,2].append(t)

                        if f_id == 1 :
                            counter_f1 += 1
                        else:
                            counter_f2 += 1
                        del remain2[f_id]
            
            sys.stdout.flush()
        for key in usage:
                logging.debug( "R1_share: %d = %d" % (key, usage[key][0]))
                logging.debug( "R2_share: %d = %d" % (key, usage[key][1]))
                
        r10 = usage[1][0]
        r11 = usage[1][1]
        r20 = usage[2][0]
        r21 = usage[2][1]
        logging.info("Flow 1 : < %.3f , %.3f > Flow 2:< %.3f , %.3f>" % (r10/(r10+r20),r11/(r11+r21),r20/(r10+r20),r21/(r11+r21)))
        logging.info("packet Thoughput %d : %d" % (counter_f1, counter_f2))
        p_counter = [counter_f1, counter_f2]
        sys.stdout.flush()
        result = [rp[0][0],rp[0][1],rp[1][0],rp[1][1],r10/(r10+r20),r11/(r11+r21),r20/(r10+r20),r21/(r11+r21),counter_f1, counter_f2]

        # for keys in start:
        #     print(keys)
        #     for i,j in zip(start[keys],end[keys]):
        #         save_to_csv([keys[1], keys[0], i, j])
                
        
        # save_to_csv(result)

def main(argv):
    global rp
    rp = argv
    print(rp)
    t = Thread(target=q_go)
    t.start()
    t1 = ffmodel()
    t1.start()
    t.join()
    t1.join()
    return p_counter


if __name__ == "__main__":
    rp = [
        [4, 2],
        [1, 2]
    ]
    main(rp)
    

    pass

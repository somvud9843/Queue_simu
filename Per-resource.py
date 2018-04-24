from queue import Queue
from queue import PriorityQueue
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

def init_output_file():
    with open('mycsvfile.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(["f_id", "p_num", "size", "time", "VST", "VFT"])

def save_to_csv(data):
    with open('mycsvfile.csv', 'a', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow([data.f_id, data.p_num, data.size, data.time, data.VST, data.VFT])


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

    def __init__(self,q, f_id, bw, size, resource_profile):
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
            p_seq += 1
            self.que.put(data.time, data)
        data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, True)
        setattr(data, "rp", self.rp)
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
        global weight
        actFL={}
        while on:
            data = self.q.get()
            # classify pakcet and update ActiveFlowList
            if not(data.f_id in actFL):
                temp_q = Queue()
                actFL[data.f_id] = temp_q
                r2Buf[data.f_id] = Queue(maxsize=0)
                setattr(actFL[data.f_id],"pVFT", 0)
            setattr(temp_q,"f_id", i)
            setattr(data,"VST", max(sys_VT, actFL[data.f_id].pVFT))
            setattr(data,"VFT", data.VST + (data.rp[0]/weight[data.f_id-1]))
            actFL[data.f_id].pVFT = data.VFT
            actFL[data.f_id].put(data)
            # save_to_csv(data)
            sys.stdout.flush()
    def stop(self):
        self.alive = False
        self.join()

class R1(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True

    def run(self):
        global sys_VT
        global mode
        global r2Buf
        global r1_usage
        t = time.clock()
        idle = True
        bf = False

        while on:
            data = []
            for keys in list(actFL):
                if r2Buf[keys].qsize() > 10:
                    bf = True
                    if not(bf):
                        logging.debug("Buffer %d : %d" % (keys, r2Buf[keys].qsize()))
                if not actFL[keys].empty() and r2Buf[keys].qsize() <= 2:
                    data.append(list(actFL[keys].queue)[0])
                    bf = False
            data = sorted(data, key=attrgetter("time"))
            try:
                next_packet = min(data, key=attrgetter("VST"))
                idle = True
            except ValueError:
                if idle:
                    idle = False
                    sys.stdout.flush()
                if self.alive:
                    continue
                else:
                    break
            except:
                print("Unexpected error:", sys.exc_info()[0])
                break
            # Remove packet i in flow i's queue and put it in r1 -> r2 buffer
            buffer = actFL[next_packet.f_id].get()

            # if not (next_packet.f_id in r1_usage):
            #     r1_usage[next_packet.f_id] = next_packet.rp[0]
            # else:
            #     r1_usage[next_packet.f_id] += next_packet.rp[0]

            logging.debug("Produce packet:%d-%d %f" % (next_packet.f_id,next_packet.p_num, time.clock()-t ))
            logging.debug(next_packet.__dict__)
            logging.debug("Update System Virtual Time: %d -> %d" % (sys_VT, next_packet.VST))
            sys_VT = next_packet.VST
            sys.stdout.flush()
            # Processing time for packet
            time.sleep(next_packet.rp[0] * speed)
            actFL[next_packet.f_id].task_done()

            setattr(buffer,"vst2", time.time())
            r2Buf[buffer.f_id].put(buffer)

    def stop(self):
        self.alive = False
        self.join()


class R2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True
        self.idle = True
        self.packet_counter = {}
        moniter = MonitorThread()
        moniter.start()

    def run(self):
        global sys_VT
        global r2Buf
        global r2_usage
        global on
        global packet_counter
        t =time.clock()
        while on:
            data = []
            for keys in list(r2Buf):
                if not r2Buf[keys].empty():
                    data.append(list(r2Buf[keys].queue)[0])
            data = sorted(data, key=attrgetter("time"))
            try:
                next_packet = min(data, key=attrgetter("vst2"))
                self.idle = True
            except ValueError:
                if self.idle:
                    self.idle = False
                    # print("Resource_2 idle...")
                continue
            except:
                print("Unexpected error:", sys.exc_info()[0])
                break
            # Remove packet i in flow i's queue
            r2Buf[next_packet.f_id].get()
            logging.debug("Produce packet(R2):%d-%d %f" % (next_packet.f_id, next_packet.p_num, time.clock() - t))

            # if not (next_packet.f_id in r2_usage):
            #     r2_usage[next_packet.f_id] = next_packet.rp[1]
            # else:
            #     r2_usage[next_packet.f_id] += next_packet.rp[1]
            if not(next_packet.f_id in usage):
                usage[next_packet.f_id] = [next_packet.rp[0]]
                usage[next_packet.f_id].append(next_packet.rp[1])
            else:
                usage[next_packet.f_id][0] += next_packet.rp[0]
                usage[next_packet.f_id][1] += next_packet.rp[1]

            # Coount the number packet been processing
            if not next_packet.f_id in self.packet_counter:
                self.packet_counter[next_packet.f_id] = 1
            else:
                self.packet_counter[next_packet.f_id] += 1

            r2Buf[next_packet.f_id].task_done()
            self.idle = False
            time.sleep(next_packet.rp[1] * speed)
            self.idle = True
            packet_counter = sum(self.packet_counter.values())
            if sum(self.packet_counter.values()) > 1000:
                on = False
            
        total_r1 = 0
        total_r2 = 0
        sorted(usage)
        for key in usage:
            total_r1 += usage[key][0]
            total_r2 += usage[key][1]
        for key in usage:
            logging.info("Flow %d <%d, %d> --- <%f, %f>" % (key, usage[key][0], usage[key][1],usage[key][0]/total_r1 ,usage[key][1]/total_r2 ))
        for keys in self.packet_counter:
            logging.info("Flow %d : %d packets" % (keys, self.packet_counter[keys]))
        sys.stdout.flush()

    def stop(self):
        self.alive = False
        self.join()


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

if __name__ == "__main__":
    global speed
    global packet_counter
    global usage
    global r2
    usage = {}
    packet_counter = 0
    speed = 10 ** -4
    on = True
    r1_usage = {}
    r2_usage = {}
    mode = "per-resource"
    # Create the shared queue and launch both threads
    start_time = time.time()
    f_num = 2
    sys_VT = 0
    # init_output_file()
    q = fifo_q()
    tList=[]
    if mode == "DRFQ":
        r2Buf = Queue()
    else:
        r2Buf = {}


    rp = [
        [15, 22],
        [13, 10]
    ]
    weight = [0.5259415,1]


    for i in range(1, f_num+1):
        t = Flow_one(q, i, 200*2**20, 256, rp[i-1])
        t.start()
        tList.append(t)

    
    # Run the consumer to dequeue
    t1 = Classifier(q)
    t1.start()
    r1 = R1()
    r1.start()
    r2 = R2()
    r2.start()
    # ff = ffModel()
    # ff.start()
    # tList.append(ff)
    tList.append(t1)
    tList.append(r1)
    tList.append(r2)

    # Make flow stop sending for x seconds. (tout = timeout)
    # tList[1].tout=






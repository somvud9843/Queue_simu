from queue import Queue
from queue import PriorityQueue
from threading import Thread
from threading import Timer, Thread, Event
import sys
import time
import random
import threading
import csv
from operator import attrgetter
import logging
import os

clear = lambda: os.system('cls')
clear()
FORMAT = " %(message)s"
logging.basicConfig(level = logging.INFO,format=FORMAT)

def init_output_file():
    with open('mycsvfile.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(["f_id", "p_num", "size", "time", "VST", "VFT"])

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
class Flow_one(Thread):

    def __init__(self,q, f_id, bw, size, resource_profile):
        Thread.__init__(self)
        self.que = q
        self.id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        # self.p_size = random.randint(160, 400)*8
        self.p_size = 50 * 8
        self.rp = resource_profile
        self.stopRequest = threading.Event()
        self.tout = 0

    def run(self):
        p_seq = 0
        while on:
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
            setattr(data,"VST", max(sys_VT,actFL[data.f_id].pVFT))
            if mode == "DRFQ":
                setattr(data,"VFT", data.VST + drpt(data))
            else:
                setattr(data, "VFT", data.VST + data.rp[0])
            actFL[data.f_id].pVFT = data.VFT
            actFL[data.f_id].put(data)
            logging.debug(data.__dict__)
            # save_to_csv(data)
            sys.stdout.flush()
            # print("Done", "There is %d packets in queue." % f_que.que.qsize())

    def stop(self):
        self.alive = False
        self.join()

# Calculate Packet i's Dominant Resource processing time
def drpt(pkt):
    DR = max(pkt.rp)
    return DR
    # Fix demand
    '''
    n = pkt.f_id
    return{
        1:4,
        2:3,
    }[n]
    '''


class R1(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True
        self.packet_counter = {}

    def run(self):
        global sys_VT
        global r2Buf
        time.sleep(0.000001)
        idle = True
        idel_counter = 0
        # while self.alive:
        while on:
            if r2Buf.qsize() > 0:
                continue
            data = []
            for keys in actFL:
                if not actFL[keys].empty():
                    data.append(list(actFL[keys].queue)[0])
            data = sorted(data, key=attrgetter("f_id"))
            try:
                next_packet = min(data, key=attrgetter("VST"))
                idle = True
            except ValueError:
                if idle:
                    idle = False
                    logging.debug("Resource_1 idle...")
                    idel_counter += 1
                    sys.stdout.flush()
                continue
            except:
                logging.error("Unexpected error:" +  sys.exc_info()[0])
                break
            # Remove packet i in flow i's queue and put it in r1 -> r2 buffer
            buffer = actFL[next_packet.f_id].get()   
            # Calulate the resource share for each flow, but here, the only packet which pass all resource take in count
            #    
            # if not(next_packet.f_id in usage):
            #     usage[next_packet.f_id] = [next_packet.rp[0]]
            # else:
            #     usage[next_packet.f_id][0] += next_packet.rp[0]

            logging.debug("(R1)Produce packet:%d-%d" % (next_packet.f_id,next_packet.p_num))
            logging.debug("Update System Virtual Time: %d -> %d" % (sys_VT, next_packet.VST))
            sys_VT = next_packet.VST
            # Processing time for packet
            time.sleep(next_packet.rp[0] * speed)
            r2Buf.put(buffer)

            # if not next_packet.f_id in packet_counter:
            #     packet_counter[next_packet.f_id] = 1
            # else:
            #     packet_counter[next_packet.f_id] += 1
            
            # self.packet_counter = packet_counter
            
        # for keys in packet_counter:
        #     logging.info("(R1)Flow %d : %d packets" % (keys, packet_counter[keys]))

    def stop(self):
        self.alive = False
        self.join()


class R2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True
        self.packet_counter = {}
        moniter = MonitorThread()
        moniter.start()

    def run(self):
        global sys_VT
        global r2Buf
        global on
        global packet_counter
        idel_counter = 0
       
        # while self.alive:
        while on:
            next_packet = r2Buf.get()

            if not(next_packet.f_id in usage):
                usage[next_packet.f_id] = [next_packet.rp[0]]
                usage[next_packet.f_id].append(next_packet.rp[1])
            else:
                usage[next_packet.f_id][0] += next_packet.rp[0]
                usage[next_packet.f_id][1] += next_packet.rp[1]

            # if len(usage[next_packet.f_id]) == 1:
            #     usage[next_packet.f_id].append(next_packet.rp[1])
            # else:
            #     usage[next_packet.f_id][1] += next_packet.rp[1]

            logging.debug("Produce packet(R2):%d-%d" % (next_packet.f_id, next_packet.p_num))
            if r2Buf.empty():
                logging.debug("Resource_2 idle...")
                idel_counter += 1
                logging.debug("Produce packet(R2):%d-%d" % (next_packet.f_id, next_packet.p_num))
            sys.stdout.flush()
            # Processing time for packet
            time.sleep(next_packet.rp[1] * speed)
            if not next_packet.f_id in self.packet_counter:
                self.packet_counter[next_packet.f_id] = 1
            else:
                self.packet_counter[next_packet.f_id] += 1
            packet_counter = sum(self.packet_counter.values())
            if sum(self.packet_counter.values()) > 1000:
                on = False
                print("%.3f" % (time.time()-start_time))
        total_r1 = 0
        total_r2 = 0
        sorted(usage)
        for key in usage:
            total_r1 += usage[key][0]
            total_r2 += usage[key][1]
        for key in usage:
            logging.info("Flow %d <%d, %d> --- <%f, %f>" % (key, usage[key][0], usage[key][1],usage[key][0]/total_r1 ,usage[key][1]/total_r2 ))
        for keys in self.packet_counter:
            logging.info("(R2)Flow %d : %d packets" % (keys, self.packet_counter[keys]))
        print(sum(self.packet_counter.values()))
        
        sys.stdout.flush()

    def stop(self):
        self.alive = False
        self.join()

class MonitorThread(Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        i = 0
        while on :
            print(i, packet_counter)
            save_to_csv([i,packet_counter])
            i += 1
            time.sleep(1)


def main(rp):
    global usage
    global mode
    global speed
    global r2Buf
    global start_time
    global sys_VT
    global packet_counter
    global on
    global filename
    filename = "data/th_DRFQ(%s,%s,%s,%s).csv" % (rp[0][0],rp[0][1],rp[1][0],rp[1][1])
    packet_counter = 0
    speed = 10 ** -3
    usage = {}
    on = True
    mode = "DRFQ"
    # Create the shared queue and launch both threads
    start_time = time.time()
    
    sys_VT = 0
    # init_output_file()
    q = fifo_q()
    tList=[]
    if mode == "DRFQ":
        r2Buf = Queue()
    else:
        r2Buf = {}
    f_num = len(rp)
    for i in range(1, f_num+1):
        t = Flow_one(q, i, 200*2**20, 400, rp[i-1])
        t.start()
        tList.append(t)

    # Run the consumer to dequeue
    t1 = Classifier(q)
    t1.start()
    r1 = R1()
    r1.start()
    r2 = R2()
    r2.start()

    tList.append(t1)
    tList.append(r1)
    tList.append(r2)
    for t in tList:
        t.join()

    
if __name__ == "__main__":
    rp = [
        [3, 3],
        [27, 4]
    ]
    main(rp)

    # Make flow stop sending for x seconds. (tout = timeout)
    # tList[1].tout=2
    # while time.time()-start_time < 21600 :
    #     print("Time:", time.time()-start_time, r1.packet_counter.items())
    #     time.sleep(1)

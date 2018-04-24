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
    with open('th_PR.csv', 'a', newline='') as f:  # Just use 'w' mode in 3.x
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
        actFL={}
        r2Buf = Queue(maxsize=0)
        while on:
            data = self.q.get()
            # classify pakcet and update ActiveFlowList
            if not(data.f_id in actFL):
                temp_q = Queue()
                actFL[data.f_id] = temp_q
                setattr(temp_q,"f_id", data.f_id)
                setattr(temp_q,"weight", weight[data.f_id-1])         
            actFL[data.f_id].put(data)
            # print(data.__dict__)
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
    def run(self):
        global sys_VT
        global mode
        global r2Buf
        global r1_usage
        # t = time.clock()
        counter = {}
        
        while on:
            fin = True
            for keys in list(actFL):
                if keys in counter:
                    counter[keys] += actFL[keys].weight
                else:
                    counter[keys] = actFL[keys].weight
                # print("set flow %d packet counter: %d" % (keys,actFL[keys].weight))
                
            while fin and not counter == {}:
                
                for keys in list(actFL):
                    if max(counter.values()) < 1 :
                        fin = False
                        break
                    if keys in counter:
                        if counter[keys]>=1:
                            next_packet = actFL[keys].get()
                            counter[keys] -= 1
                            
                            # print("Produce packet:%d-%d %f" % (next_packet.f_id,next_packet.p_num, time.clock()))
                            # logging.debug(next_packet.__dict__)
                            if actFL[keys].empty():
                                del actFL[keys]
                            # Remove packet i in flow i's queue and put it in r1 -> r2 buffer
                            buffer = next_packet
                            # sys_VT = next_packet.VST
                            sys.stdout.flush()
                            # Processing time for packet
                            time.sleep(next_packet.rp[0] * speed)
                            
                            r2Buf.put(buffer)
                        

                    

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
            next_packet = r2Buf.get()
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

            r2Buf.task_done()
            self.idle = False
            time.sleep(next_packet.rp[1] * speed)
            self.idle = True
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
            logging.info("Flow %d : %d packets" % (keys, self.packet_counter[keys]))
        sys.stdout.flush()

    def stop(self):
        self.alive = False
        self.join()

class ffModel(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True

    def run(self):
        remain = {}
        remain2 = {}
        packet = {}
        usage = {}
        t = 1 
        buf = {}
        while t<3*10**2:
            for keys in actFL:
                if not keys in buf:
                    buf[keys] = None
                if buf[keys] == None:
                    if not keys in remain.keys():
                        if not actFL[keys].empty():
                            packet[keys] = actFL[keys].get()
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
          
            t += 1
            time.sleep(0.001)

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
            
        r10 = usage[1][0]
        r11 = usage[1][1]
        r20 = usage[2][0]
        r21 = usage[2][1]
        print("R1 : < %f , %f > R2:< %f , %f>" % (r10/(r10+r20),r11/(r11+r21),r20/(r10+r20),r21/(r11+r21)))
        sys.stdout.flush()

    def stop(self):
        self.alive = False
        self.join()

class MonitorThread(Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global packet_counter
        i = 0
        while on:
            print(i,packet_counter)
            save_to_csv([i, packet_counter])
            i += 1
            time.sleep(1)

def main():
    global speed
    global packet_counter
    global usage
    global r2
    global weight 
    global on
    global start_time
    global r2Buf

    packet_counter = 0
    usage = {}
    packet_counter = {}
    speed = 10 ** -3
    on = True
    # Create the shared queue and launch both threads
    start_time = time.time()
    f_num = 2
    # init_output_file()
    q = fifo_q()
    tList=[]
    r2Buf = Queue()
    rp = [
        [22, 20],
        [17, 23]
    ]

    weight = [1.149151,1]
    for i in range(1, f_num+1):
        t = Flow_one(q, i, 200*2**20, 512, rp[i-1])
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


if __name__ == "__main__":
    main()







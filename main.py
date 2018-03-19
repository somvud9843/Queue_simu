from queue import Queue
from queue import PriorityQueue
from threading import Thread
import sys
import time
import random
import threading
import csv
from operator import attrgetter

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
        while self.alive:
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
        while self.alive:
            data = self.q.get()
            # classify pakcet and update ActiveFlowList
            if not(data.f_id in actFL):
                temp_q = Queue()
                actFL[data.f_id] = temp_q
                r2Buf[data.f_id] = Queue(maxsize=0)
                setattr(actFL[data.f_id],"pVFT", 0)
            setattr(temp_q,"f_id", i)
            setattr(data,"VST", max(sys_VT, actFL[data.f_id].pVFT))
            if mode == "DRFQ":
                setattr(data,"VFT", data.VST + drpt(data))
            else:
                setattr(data, "VFT", data.VST + data.rp[0])
            actFL[data.f_id].pVFT = data.VFT
            actFL[data.f_id].put(data)
            # print(data.__dict__)
            # save_to_csv(data)
            sys.stdout.flush()
            # print("Done", "There is %d packets in queue." % f_que.que.qsize())
        for keys in actFL:
            print("Flow %d Queue Length: %d" %(keys, actFL[keys].qsize()))

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
        time.sleep(0.000001)
        idle = True

        while self.alive:
            data = []
            for keys in actFL:
                if not actFL[keys].empty() and r2Buf[keys].qsize() <= 1:
                    data.append(list(actFL[keys].queue)[0])
            data = sorted(data, key=attrgetter("time"))
            try:
                next_packet = min(data, key=attrgetter("VST"))
                idle = True
            except ValueError:
                if idle:
                    idle = False
                    # print("Resource_1 idle...")
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

            if not (next_packet.f_id in r1_usage):
                r1_usage[next_packet.f_id] = next_packet.rp[0]
            else:
                r1_usage[next_packet.f_id] += next_packet.rp[0]

            print("Produce packet:%d-%d" % (next_packet.f_id,next_packet.p_num), end="")
            print(next_packet.__dict__)
            # print("Update System Virtual Time: %d -> %d" % (sys_VT, next_packet.VST))
            sys_VT = next_packet.VST
            sys.stdout.flush()
            # Processing time for packet
            time.sleep(next_packet.rp[0] * speed)
            actFL[next_packet.f_id].task_done()
            counter[0] += 1
            if mode == "DRFQ":
                r2Buf.put(buffer)
            else:
                # print("buffer %d queue now: %d." % (buffer.f_id, r2Buf[buffer.f_id].qsize()))
                # if r2Buf[buffer.f_id].qsize() >= 1:
                    # print("FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUULLLLLLLLLLLLLLLL")
                r2Buf[buffer.f_id].put(buffer)

    def stop(self):
        self.alive = False
        print(self, "Stop...")
        self.join()


class R2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.alive = True

    def run(self):
        global sys_VT
        global r2Buf
        global r2_usage
        idle = True
        start_time = time.time()
        while self.alive:
            if mode == "DRFQ":
                next_packet = r2Buf.get()
                if not (next_packet.f_id in r2_usage):
                    r2_usage[next_packet.f_id] = next_packet.rp[1]
                else:
                    r2_usage[next_packet.f_id] += next_packet.rp[1]
                print("Produce packet(R2):%d-%d" % (next_packet.f_id, next_packet.p_num))
                # if r2Buf.empty():
                #     # print("Resource_2 idle...")
            else:
                data = []
                for keys in r2Buf:
                    if not r2Buf[keys].empty():
                        data.append(list(r2Buf[keys].queue)[0])
                data = sorted(data, key=attrgetter("time"))
                try:
                    next_packet = min(data, key=attrgetter("VFT"))
                    idle = True
                except ValueError:
                    if idle:
                        idle = False
                        idleCounter = time.time() - start_time
                        # print("Resource_2 idle...")
                    continue
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    break
                # Remove packet i in flow i's queue
                r2Buf[next_packet.f_id].get()
                print("Produce packet(R2):%d-%d" % (next_packet.f_id, next_packet.p_num))

                if not (next_packet.f_id in r2_usage):
                    r2_usage[next_packet.f_id] = next_packet.rp[1]
                else:
                    r2_usage[next_packet.f_id] += next_packet.rp[1]
                r2Buf[next_packet.f_id].task_done()
            time.sleep(next_packet.rp[1] * speed)
            
            print (next_packet.f_id)
            if next_packet.f_id == 1 :
                counter[0] += 1
            else:
                counter[1] += 1
        for keys in r1_usage:
            print("--" * 50, "R1_share: %d = %d" % (keys, r1_usage[keys]))
            print("--" * 50, "R2_share: %d = %d" % (keys, r2_usage[keys]))
        f10 = r1_usage[1]
        f11 = r2_usage[1]    
        f20 = r1_usage[2]
        f21 = r2_usage[2]
        print("R1 : < %f , %f > R2:< %f , %f>" % (f10/(f10+f20),f11/(f11+f21),f20/(f10+f20),f21/(f11+f21)))
        print("packet throughput: %d : %d" % (counter[0],counter[1] ))
        sys.stdout.flush()
        # Processing time for packet

    def stop(self):
        self.alive = False
        self.join()
        print(self, "Stop")

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
                        print("R1----------packet %d Done at %d." % (f_id, t ))
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

if __name__ == "__main__":
    global on
    global speed
    global counter
    counter= [0,0]
    speed = 10 ** -3
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
        [20, 1],
        [10, 11]
    ]
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
    # ff = ffModel()
    # ff.start()
    # tList.append(ff)
    tList.append(t1)
    tList.append(r1)
    tList.append(r2)

    # Make flow stop sending for x seconds. (tout = timeout)
    # tList[1].tout=2

    time.sleep(2)
    # for key in r1_usage:
    #     print("--" * 50, "R1_share: %d = %d" % (key, r1_usage[key]))
    #     print("--" * 50, "R2_share: %d = %d" % (key, r2_usage[key]))

    for t in tList:
        t.stop()
        print("Stop %s"%(t))







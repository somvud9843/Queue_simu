from queue import Queue
from queue import PriorityQueue
from threading import Thread
import sys
import time
import random
import threading


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

class Flow(Thread):

    def __init__(self,q, f_id, bw, size):
        Thread.__init__(self)
        self.que = q
        self.id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = random.randint(160, 400)
        self.stopRequest = threading.Event()
        self.tout = 0

    def run(self):
        p_seq = 0
        while p_seq < 7:

            if self.tout > 0:
                print("Flow %d stop sending for %d seconds" % (self.id, self.tout))
                time.sleep(self.tout)
                self.tout = 0

            # Produce some data
            time.sleep(self.p_size / self.bw) # transmission delay
            # time.sleep(1)
            data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, False)
            p_seq += 1
            self.que.put(data.time, data)
        data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, True)
        self.que.put(data.time, data)


# FIFO queue
class Flow_one(Thread):

    def __init__(self, q, f_id, bw, size):
        Thread.__init__(self)
        self.que = q
        self.f_id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = size #random.randint(160, 400)
        self.stopRequest = threading.Event()
        self.tout = 0
        self.__vt = 0

    def run(self):
        p_seq = 0
        while p_seq < 100:
            if self.tout > 0:
                print("Flow %d stop sending for %d seconds" % (self.f_id, self.tout))
                time.sleep(self.tout)
                self.tout = 0
            # Produce some data
            # print(self.f_id, "  Delay = ", self.p_size / self.bw)
            time.sleep(self.p_size / self.bw) # transmission delay
            data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, False)
            p_seq += 1
            self.que.put(data.time, data)

        data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, True)
        self.que.put(data.time, data)

    def setvt(self, t):
        self.__vt = t

    def getvt(self):
        return self.__vt


# A thread that consumes data
# Round robin scheduling


def consumer(fList):
    f_flow = 0  # Finished flow counter
    actFL = {} # ActiveFlowList: Dictionray type
    while f_flow != f_num:
        # Get some data
        for f_que in fList:
            data = f_que.que.get()

            print(data.__dict__)
            sys.stdout.flush()
            # print("Done", "There is %d packets in queue." % f_que.que.qsize())
            if data.isLast:
                f_flow += 1

# consumer of fifo queue


    
def pq(q):
    f_flow = 0  # Finished flow counter
    sys_VT = 0
    actFL={}
    while f_flow != f_num:
        data = q.get()
        # classify pakcet and update ActiveFlowList
        if not(data.f_id in actFL):
            temp_q = Queue()
            actFL[data.f_id] = temp_q
            setattr(actFL[data.f_id],"pVFT", 0)
        setattr(temp_q,"f_id", i)
        setattr(data,"VST", max(sys_VT,actFL[data.f_id].pVFT))
        setattr(data,"VFT", data.VST + drpt(data))
        actFL[data.f_id].pVFT = data.VFT
        actFL[data.f_id].put(data)
        
        sys_VT = data.VST
        print(data.__dict__)
        sys.stdout.flush()
        time.sleep(0.001)
        # print("Done", "There is %d packets in queue." % f_que.que.qsize())
        if data.isLast:
            f_flow += 1

#Calculate Packet i's Dominatent Resource porcessing time
def drpt(pkt):
    n = pkt.f_id
    return{
        1:4,
        2:3,
    }[n]
    

# Create the shared queue and launch both threads

global f_num
global start_time

# System's virtual time
start_time = time.time()
f_num = 2

# t = Flow(1, 100*2**20, 512)
# t.start()
# t.join

q = fifo_q()
tList=[]
for i in range(1, f_num+1):
    t = Flow(q, i, 100*2**10, 512)
    # t = Flow_one(q, i, 100*2**10, 512)
    t.start()
    tList.append(t)


# Run the consumer to dequeue
t1 = Thread(target=pq, args=(q,))
t1.start()
# Make flow stop send for x second. tout = timeout
# tList[0].tout=5

t1.join()


time.sleep(2)

for t in tList:
    t.stopRequest.set()

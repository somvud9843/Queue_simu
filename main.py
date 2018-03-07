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
        self.flow_id = flow_id
        self.p_num = p_num
        self.size = size
        self.time = g_time
        self.isLast = isLast
# A thread that produces data


class Flow(Thread):

    def __init__(self, f_id, bw, size):
        Thread.__init__(self)
        self.que = Queue()
        self.f_id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = random.randint(160, 400)
        self.stopRequest = threading.Event()

    def run(self):
        p_seq = 0
        while p_seq < 100:
            # Produce some data
            # transmission delay
            # print(self.f_id, "  Delay = ", self.p_size / self.bw)
            time.sleep(self.p_size / self.bw)
            data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, False)
            p_seq += 1
            self.que.put(data)

        data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, True)
        self.que.put(data)


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
        while p_seq < 1000:
            if self.tout >= 0:
                time.sleep(self.tout)
                self.tout = 0
            # Produce some data
            # transmission delay
            # print(self.f_id, "  Delay = ", self.p_size / self.bw)
            time.sleep(self.p_size / self.bw)
            data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, False)
            p_seq += 1
            self.que.put(data.time, data)

        data = Packet(self.f_id, p_seq, self.p_size, time.time()-start_time, True)
        self.que.put(data.time, data)

    def setvt(self, t):
        self.__vt = t

    def getvt(self):
        return self.__vt


def flow2(out_q):
    f_id = 2
    id = 0
    # Bandwidth(bps) 100 * M(2^20)
    bw = 100 * 2**20
    # Packet Size(bits)
    p_size = 512
    p_last = False
    while not p_last:
        # Produce some data
        if id >= 99:
            data = Packet(f_id, id, p_size, time.time(), True)

            p_last = True
        else:
            data = Packet(f_id, id, p_size, time.time(), False)
        id += 1
        # transmission delay
        time.sleep(p_size / bw)
        out_q.put(data)

# A thread that consumes data
# Round robin scheduling


def consumer(fList):
    f_flow = 0  # Finished flow counter
    idle_c = 0
    wing = 0
    sche = PriorityQueue()
    while f_flow != f_num:
        # Get some data
        for f_que in fList:
            data = f_que.que.get()
            sche.put(data.time, data)
            print(data.__dict__)
            sys.stdout.flush()
            time.sleep(0.001)
            # print("Done", "There is %d packets in queue." % f_que.que.qsize())
            if data.isLast:
                f_flow += 1

    print("Idle", idle_c, "working", wing)

# consumer of fifo queue


def pq(q):
    f_flow = 0  # Finished flow counter
    while f_flow != f_num:
        # Get some data
        data = q.get()
        cvt = data.time()
        print(data.__dict__)
        sys.stdout.flush()
        time.sleep(0.001)
        # print("Done", "There is %d packets in queue." % f_que.que.qsize())
        if data.isLast:
            f_flow += 1

# Create the shared queue and launch both threads

global f_num
global start_time
start_time = time.time()
f_num = 2

# t = Flow(1, 100*2**20, 512)
# t.start()
# t.join

q = fifo_q()
tList=[]
for i in range(1, f_num+1):
    # t = Flow(i, 100*2**10, 512)
    t = Flow_one(q, i, 100*2**10, 512)
    t.start()
    tList.append(t)



# q2= Queue()

# Run the consumer to dequeue

# t1 = Thread(target=consumer, args=(tList,))
t1 = Thread(target=pq, args=(q,))
t1.start()
tList[0].tout=3

t1.join()


time.sleep(2)

for t in tList:
    t.stopRequest.set()
'''
t2 = Thread(target=flow1, args=(q,))
t3 = Thread(target=flow2, args=(q,))

t2.start()
t3.start()

t2.join()
t3.join()
'''
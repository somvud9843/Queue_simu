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

class Flow(Thread):

    def __init__(self,q, f_id, bw, size):
        Thread.__init__(self)
        self.que = q
        self.id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = random.randint(160, 400)*8
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
            # time.sleep(self.p_size / self.bw) # transmission delay
            time.sleep(0.1)
            data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, False)
            p_seq += 1
            self.que.put(data.time, data)
        data = Packet(self.id, p_seq, self.p_size, time.time()-start_time, True)
        self.que.put(data.time, data)


# Queue with resource profile
class Flow_one(Thread):

    def __init__(self,q, f_id, bw, size, resource_profile):
        Thread.__init__(self)
        self.que = q
        self.id = f_id
        # Bandwidth(bps) 100 * M(2^20)
        self.bw = bw
        # Packet Size(bits)
        self.p_size = random.randint(160, 400)*8
        self.rp = resource_profile
        self.stopRequest = threading.Event()
        self.tout = 0

    def run(self):
        p_seq = 0
        while p_seq < 7:
            if self.tout > 0:
                self.sleep()

            # Produce some data
            # time.sleep(self.p_size / self.bw) # transmission delay
            time.sleep(0.1)
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
    global sys_VT
    global actFL
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
        
        
        print(data.__dict__)
        # save_to_csv(data)
        sys.stdout.flush()
        # print("Done", "There is %d packets in queue." % f_que.que.qsize())
        if data.isLast:
            f_flow += 1

#Calculate Packet i's Dominatent Resource porcessing time
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
def r1():
    global sys_VT
    time.sleep(0.000001)
    idle = True
    while True:
        data = []
        for keys in actFL:
            if not actFL[keys].empty():
                data.append(list(actFL[keys].queue)[0])
        data = sorted(data, key= attrgetter("f_id"))
        try:
            next_packet = min(data,key=attrgetter("VST"))
            idle = True
        except ValueError:
            if idle:
                idle = False
                print("Resource_1 idle...")
                sys.stdout.flush()
            continue
        except:
            print("Unexpected error:", sys.exc_info()[0])
            break
        # Remove packet i in flow i's queue 
        actFL[next_packet.f_id].get()
        print("Produce packet:%d-%d" % (next_packet.f_id,next_packet.p_num))
        print("Update System Virtual Time: %d -> %d" % (sys_VT, next_packet.VST))
        sys_VT = next_packet.VST
        sys.stdout.flush()
        # Processing time for packet
        time.sleep(0.25)
            # if actFL[next_packet.f_id].empty():
            #     del actFL[next_packet.f_id]
    
if __name__ == "__main__":
    # Create the shared queue and launch both threads
    start_time = time.time()
    f_num = 2
    sys_VT = 0
    # init_output_file()
    q = fifo_q()
    tList=[]
    rp = [
        [4, 1],
        [1, 3]
    ]
    for i in range(1, f_num+1):
        if 1:
            t = Flow_one(q, i, 200*2**20, 512, rp[i-1])
        else:
            t = Flow(q, i, 200*2**20, 512)
        t.start()
        tList.append(t)
    

    # Run the consumer to dequeue
    t1 = Thread(target=pq, args=(q,))
    t1.start()

    r = Thread(target=r1)
    r.start()
    # Make flow stop sending for x seconds. (tout = timeout)
    time.sleep(0.4)
    tList[1].tout=2
    t1.join()

    time.sleep(7)

    for t in tList:
        t.stopRequest.set()




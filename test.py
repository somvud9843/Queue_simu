from queue import Queue
import time

class Packet:

    def __init__(self, flow_id, p_num, size, g_time, isLast):
        self.flow_id = flow_id
        self.p_num = p_num
        self.size = size
        self.time = g_time
        self.isLast = isLast

q = Queue()
for i in range(1,10):
    p = Packet(1, i, 123, time.time(), False)
    q.put(p)
data = list(q.queue)[0]
print(data)

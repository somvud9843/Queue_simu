from queue import Queue
import time
from operator import attrgetter

class Packet:

    def __init__(self, flow_id, p_num, size, g_time, isLast):
        self.flow_id = flow_id
        self.p_num = p_num
        self.size = size
        self.arr_time = g_time
        self.isLast = isLast

# q = Queue()
def main():
    qDict = {}
    data = []
    for i in range(1,3):
        qDict[i] = Queue()
        for j in range(1,10):
            p = Packet(1, j, 123, time.time(), False)
            qDict[i].put(p)
    print(qDict[1])
    for i in qDict:
        data.append(list(qDict[i].queue)[0])
        # print(data.__dict__)
    print( min(data,key=attrgetter("arr_time")).p_num)

if __name__ == "__main__":
    main()

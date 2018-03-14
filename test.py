from queue import Queue
import time
from operator import attrgetter
from sympy import *
from fractions import Fraction
import numpy as np

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
    for i in range(2):
        qDict[i] = Queue(maxsize=1)
        for j in range(1,10):
            p = Packet(i, j, 123, time.time(), False)
            if qDict[i].full():
                print("Queue %d is FULL, waiting for space..." % (i))
                qDict[i].get()
            print("Queue %d put new data %d."% (i,j))
            qDict[i].put(p)
    qqq =Queue()
    for j in range(10):
        p = Packet(i, j, 123, time.time(), False)
        qqq.put(p)
    print(qqq.qsize())
    qqq.get()
    print(qqq.qsize())

def dict_list():
    dict={}
    for i in range(3):
        dict[i] = [0, i]

    print(dict[1][1])
def slove_funtion():
    x = Symbol('x', positive=True)
    y = Symbol('y', positive=True)



    f=Fraction(4, 2)


    print(4/f, 2/f)
    f1 = 2 * x + 1 * y - 1
    f2 = x + 2 * y - 1
    sol = solve((f1, f2), x, y)
    print(sol)
    # OUT: {x: 50, y: 30, z: 20}

if __name__ == "__main__":
    main()

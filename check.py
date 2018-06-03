import random
from sympy import *
import csv
import ffmodel
import time

def save_to_csv(data):
    with open('calc.csv', 'a', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f, delimiter =',',quotechar ="'",quoting=csv.QUOTE_MINIMAL)
        w.writerow(data)

def gcd(m, n):
    return m if n == 0 else gcd(n, m % n)

def check(f1, f2):
    mode = "P"
    result = []

    print("Set %s : [%d, %d], [%d, %d]" % (keys, f1[0], f1[1], f2[0], f2[1]))
    result = [f1[0], f1[1], f2[0], f2[1]]

    temp1 = f1.copy()
    temp2 = f2.copy()
    gcd_num = gcd(f1[0], f2[0])
    for index, item in enumerate(f1):
        temp1[index] = item * f2[0]/gcd_num
    for index, item in enumerate(f2):
        temp2[index] = item * f1[0]/gcd_num
    if temp1[0]+temp2[0] > temp1[1]+temp2[1] or (temp1[0] == temp2[0] and temp1[1] == temp2[1]):
        mode = "B"
        print("Bf1:<%.3f, %.3f>  f2:<%.3f, %.3f>" % (temp1[0]/(temp1[0]+temp2[0]), temp1[1]/(temp1[1]+temp2[1]), temp2[0]/(temp1[0]+temp2[0]), temp2[1]/(temp1[1]+temp2[1])))
        result.extend([temp1[0]/(temp1[0]+temp2[0]), temp1[1]/(temp1[1]+temp2[1]), temp2[0]/(temp1[0]+temp2[0]), temp2[1]/(temp1[1]+temp2[1])])
    else:
        gcd_num = gcd(f1[1], f2[1])
        for index, item in enumerate(f1):
            temp1[index] = item * f2[1]/gcd_num
        for index, item in enumerate(f2):
            temp2[index] = item * f1[1]/gcd_num
        if temp1[0]+temp2[0] < temp1[1]+temp2[1]:
            mode = "B"
            print("Bf1:<%.3f, %.3f>  f2:<%.3f, %.3f>" % (temp1[0]/(temp1[0]+temp2[0]), temp1[1]/(temp1[1]+temp2[1]), temp2[0]/(temp1[0]+temp2[0]), temp2[1]/(temp1[1]+temp2[1])))
            result.extend([temp1[0]/(temp1[0]+temp2[0]), temp1[1]/(temp1[1]+temp2[1]), temp2[0]/(temp1[0]+temp2[0]), temp2[1]/(temp1[1]+temp2[1])])
    if mode == "P":
        x = Symbol('x')
        y = Symbol('y')
        ans = solve([f1[0]*x + f2[0]*y - 1, f1[1]*x + f2[1]*y - 1], [x, y])
        
        print(ans)
        print("Pf1:<%.3f, %.3f>  f2:<%.3f, %.3f>"% (ans[x]*f1[0], ans[x]*f1[1], ans[y]*f2[0],ans[y]*f2[1]))
        result.extend([float(ans[x]*f1[0]), float(ans[x]*f1[1]), float(ans[y]*f2[0]),float(ans[y]*f2[1])])
    # save_to_csv(result)
dv = {}
for i in range(0) :
    dv[i] = []
    for j in range(2):
        r1 = random.randint(1,30)
        r2 = random.randint(1,30)
        dv[i].append([r1, r2])

# dv["sample"] =[
#     [4,2],[1,2]
#     ] 
# dv["test0"] = [
#     [3,5],[2,1]
#     ]
# dv["test1"] = [
#     [22, 29], [15, 14]
#     ]
# dv["test2"] = [
#     [7, 9], [17, 8]
#     ]
# dv["test3"] = [
#     [6, 4], [4, 10]
#     ]
# dv["test3-1"] = [
#     [7, 4], [4, 10]
#     ]
# dv["test4"] = [
#     [11, 6], [6, 20]
#     ]
# dv["test5"] = [
#     [16, 24], [10, 8]
#     ]  
# dv["test5-1"] = [
#     [16, 24], [11, 8]
#     ]

for i in range(1,22,1):
    dv[i]=[
        [i, 22],
        [13, 10]
    ]


for keys in dv:
    f1 = dv[keys][0]
    f2 = dv[keys][1]
    check(f1, f2)
    # test.main(dv[keys])
    # time.sleep(3)
    # print("Set %s : [%d, %d], [%d, %d]" % (keys, dv[keys][0][0], dv[keys][0][1], dv[keys][1][0], dv[keys][1][1]))
    



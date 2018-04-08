import random
from sympy import *

def check(f1, f2):
    mode = "P"

    if f1[0]+f2[0] > f1[1]+f2[1]:
        # print("Bottleneck: R1")
        if (f1[1]-f2[1])/2 + min(f1[1], f2[1]) <= min(f1[0], f2[0]):
            mode = "B"
    elif f1[0]+f2[0] == f1[1]+f2[1]:
        print("Same Bottleneck")
    else:
        # print("Bottleneck: R2")
        if (f1[0]-f2[0])/2 + min(f1[0], f2[0]) <= min(f1[1], f2[1]):
            mode = "B"

    if f1[0] == f1[1] or f2[0] == f2[1]:
        mode = "B"

    if mode == "P":
        x = Symbol('x')
        y = Symbol('y')
        ans = solve([f1[0]*x + f2[0]*y - 1, f1[1]*x + f2[1]*y - 1], [x, y])
        print(ans)
        print("f1:<%.3f, %.3f>  f2:<%.3f, %.3f>"% (ans[x]*f1[0], ans[x]*f1[1], ans[y]*f2[0],ans[y]*f2[1]))

dv = {}
for i in range(4) :
    dv[i] = []
    for j in range(2):
        r1 = random.randint(1,30)
        r2 = random.randint(1,30)
        dv[i].append([r1, r2])
dv["test"] = [
    [13, 20], [6, 3]
    ]
for keys in dv:
    f1 = dv[keys][0]
    f2 = dv[keys][1]
    print("Set %s : [%d, %d], [%d, %d]" % (keys, dv[keys][0][0], dv[keys][0][1], dv[keys][1][0], dv[keys][1][1]))
    check(f1, f2)



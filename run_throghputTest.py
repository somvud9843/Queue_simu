import csv
import DRFQ
import WRR
import PR
import ffmodel

def read_csv():
    table = []
    with open('result.csv','r', newline='') as csvfile:

        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            temp = row[0].split(',')
            table.append(temp)
    return table

table = read_csv()

for data in table:
    rp = [
        [int(data[0]), int(data[1])],
        [int(data[2]), int(data[3])]
        ]
    # weight = float(data[20])
    # DRFQ.main(rp)
    # PR.main(rp,weight)
    # WRR.main(rp, weight)
rp = [
    [8,27],
    [12,10]
]
# 0.370426203

result = ffmodel.main(rp)
weight = (result[0]/result[1])/(rp[1][0]/rp[0][0])
print(weight)


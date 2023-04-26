# importing csv module
import csv
import matplotlib.pyplot as plt
import numpy as np
import os

llc_sets = [512, 2048, 8192, 32768]
llc_repl = ["lru", "lip", "eaf", "hawkeye", "lfu"]
TRACES = os.listdir("gap_traces")

data = np.zeros((2, len(TRACES), len(llc_repl), len(llc_sets)))

filename = "results/llc_set_size/llc_set_size.csv"
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting each data row one by one
    i1 = 0
    i2 = 0
    i3 = 0
    for row in csvreader:
        i1 = (csvreader.line_num - 1) % 2
        i2 = (csvreader.line_num - 1) / 8
        if (csvreader.line_num - 1) % 8 <= 1:
            i3 = 0
        elif (csvreader.line_num - 1) % 8 <= 3:
            i3 = 1
        elif (csvreader.line_num - 1) % 8 <= 5:
            i3 = 2
        else:
            i3 = 3
        data[0][int(i1)][int(i2)][int(i3)] = row[3]
        data[1][int(i1)][int(i2)][int(i3)] = row[4]
 
ind = np.arange(len(llc_repl))
width = 0.1

# print(ind)
# print(data[0])

for i in range(len(TRACES)):
    data[0][i] = data[0][i]/data[0][i][0][1]
    data[1][i] = data[1][i]/data[1][i][0][1]

    for k in range(len(llc_sets)):
        plt.bar(ind + width*k, data[0][i, :, k], width, label=llc_sets[k])

    plt.xticks(ind+ width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend()
    plt.title("Effect on IPC with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"results/llc_set_size/pics/{TRACES[i][:-3]}_ipc.png")
    plt.close()

    for k in range(len(llc_sets)):
        plt.bar(ind + width*k, data[1][i, :, k], width, label=llc_sets[k])

    plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend()
    plt.title("Effect on hit rate with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"results/llc_set_size/pics/{TRACES[i][:-3]}_hit.png")
    plt.close()


    # for k in range(len(llc_sets)):
    #     plt.bar(ind + width*k, data[2][i, :, k], width, label=llc_sets[k])

    # plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    # plt.legend()
    # plt.title("Effect on MPKI with different LLC replacement policies")
    # # plt.show()
    # plt.savefig(f"results/llc_set_ways/pics/{TRACES[i][:-3]}_mpki.png")
    # plt.close()

           
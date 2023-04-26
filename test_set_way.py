import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
from pwn import *

llc_ways = [1, 4, 16, 64]
iter = 30000000
llc_repl = ["lru", "lip", "eaf", "gippr", "random", "fifo", "drrip", "srrip", "ship", "lfu"]

to_run = int(sys.argv[1])
curr_running = []
sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open("results/llc_set_ways/llc_set_ways.csv", "a")

data = np.zeros((2, len(TRACES), len(llc_repl), len(llc_ways)))

os.system("cp non_inclusive.cc src/cache.cc")

for k, repl in enumerate(llc_repl):
    if to_run:
        sim_config['LLC']['replacement'] = repl
    
    for j, way in enumerate(llc_ways):
        if to_run:
            sim_config["executable_name"] = "bin/champsim"
            sim_config["LLC"]["sets"] = sim_config["LLC"]["sets"] * sim_config["LLC"]["ways"] // way
            sim_config["LLC"]["ways"] = way

            json.dump(sim_config, open('my_config.json', 'w'))

            os.system("./config.sh my_config.json")
            os.system("make")
        for i, trace in enumerate(TRACES):
            if to_run:
                curr_running.append(process(argv=["./single_runner.sh", f"{iter}", f"{trace}", f"results/llc_set_ways/{trace[:-3]}_{repl}_{way}.txt"]))

            # llc_info = os.popen(f'grep "LLC TOTAL" results/llc_set_ways/{trace[:-3]}_{repl}_{way}.txt').read().split()
            # llc_hit = int(llc_info[5])/int(llc_info[3])
            # ipc = os.popen(f'grep "CPU 0 cumulative IPC" results/llc_set_ways/{trace[:-3]}_{repl}_{way}.txt').read().split()[4]
            # mpki = int(llc_info[7])/int(ipc[6])*1000
            # ipc = ipc[4]

            # if to_run:
            #     out_file.write(f"{trace[:-3]},{repl},{way},{ipc},{llc_hit}\n")
            # data[0][i][k][j] = ipc
            # data[1][i][k][j] = llc_hit
            # # data[2][i][k][j] = mpki


for p in curr_running:
    p.wait_for_close()


# ind = np.arange(len(llc_repl))
# width = 0.1

# print(ind)
# print(data[0])

# for i in range(len(TRACES)):
#     data[0][i] = data[0][i]/data[0][i][0][0]
#     data[1][i] = data[1][i]/data[1][i][0][0]

#     for k in range(len(llc_sets)):
#         plt.bar(ind + width*k, data[0][i, :, k], width, label=llc_sets[k])

#     plt.xticks(ind+ width*(len(llc_repl) - 1) /2 , llc_repl)
#     plt.legend()
#     plt.title("Effect on IPC with different LLC replacement policies")
#     # plt.show()
#     plt.savefig(f"temp/pics/{TRACES[i][:-3]}_ipc.png")
#     plt.close()

#     for k in range(len(llc_sets)):
#         plt.bar(ind + width*k, data[1][i, :, k], width, label=llc_sets[k])

#     plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
#     plt.legend()
#     plt.title("Effect on hit rate with different LLC replacement policies")
#     # plt.show()
#     plt.savefig(f"temp/{TRACES[i][:-3]}_hit.png")
#     plt.close()


#     # for k in range(len(llc_sets)):
#     #     plt.bar(ind + width*k, data[2][i, :, k], width, label=llc_sets[k])

#     # plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
#     # plt.legend()
#     # plt.title("Effect on MPKI with different LLC replacement policies")
#     # # plt.show()
#     # plt.savefig(f"temp/pics/{TRACES[i][:-3]}_mpki.png")
#     # plt.close()


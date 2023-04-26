#!/usr/bin/python
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

to_run = int(sys.argv[1])

NUM_INSTR = 30000000


cache_policy = ["inclusive" ,"non_inclusive", "exclusive"]
llc_repl = ["lru", "lip", "eaf", "gippr", "random", "fifo", "drrip", "srrip", "ship", "hawkeye", "lfu"]

result_dir = "results/inc_exc"
# llc_repl = [ ]

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open(f"{result_dir}/llc_repl.csv", "a", buffering=10)

data = np.zeros((3, len(TRACES), len(llc_repl), len(cache_policy)))

for k, policy in enumerate(cache_policy):

    os.system(f"cp {policy}.cc src/cache.cc")

    for j, repl in enumerate(llc_repl):
        if to_run:
            sim_config["executable_name"] = "bin/champsim"
            sim_config["LLC"]["replacement"] = repl

            json.dump(sim_config, open('my_config.json', 'w'))

            os.system("./config.sh my_config.json")
            os.system("make")

        for i, trace in enumerate(TRACES):
            res_file = f"{result_dir}/{trace[:-3]}_{policy}_{repl}.txt"
            if to_run:
                os.system(f"bin/champsim -warmup_instructions {NUM_INSTR} -simulation_instructions {NUM_INSTR} gap_traces/{trace} > {res_file}")

            llc_info = os.popen(f'grep "LLC TOTAL" {res_file}').read().split()
            ipc = os.popen(f'grep "CPU 0 cumulative IPC" {res_file}').read().split()
            mpki = int(llc_info[7])/int(ipc[6])*1000
            llc_hit = int(llc_info[5])/int(llc_info[3])
            ipc = ipc[4]
            
            if to_run:
                out_file.write(f"{trace[:-3]},{policy},{repl},{ipc},{llc_hit},{mpki}\n")
            data[0][i][j][k] = ipc
            data[1][i][j][k] = llc_hit
            data[2][i][j][k] = mpki
        
ind = np.arange(len(llc_repl))
width = 0.1

# print(ind)
# print(data[0])

for i in range(len(TRACES)):
    data[0][i] = data[0][i]/data[0][i][0][0]
    data[1][i] = data[1][i]/data[1][i][0][0]

    for k in range(len(cache_policy)):
        plt.bar(ind + width*k, data[0][i, :, k], width, label=cache_policy[k])

    plt.xticks(ind+ width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend(loc = 'lower right')
    plt.title("Effect on IPC with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_ipc.png")
    plt.close()

    for k in range(len(cache_policy)):
        plt.bar(ind + width*k, data[1][i, :, k], width, label=cache_policy[k])

    plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend(loc = 'lower right')
    plt.title("Effect on hit rate with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_hit.png")
    plt.close()


    for k in range(len(cache_policy)):
        plt.bar(ind + width*k, data[2][i, :, k], width, label=cache_policy[k])

    plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend(loc = 'lower right')
    plt.title("Effect on MPKI with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_mpki.png")
    plt.close()

#!/usr/bin/python
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

to_run = int(sys.argv[1])

NUM_INSTR = 1000000

llc_repl = ["lru", "lip", "eaf", "gippr", "random", "fifo", "drrip", "srrip"]
# llc_repl = [ ]

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open("results/repl/llc_repl.csv", "a")

data = np.zeros((2, len(TRACES), len(llc_repl)))

for j, repl in enumerate(llc_repl):
    if to_run:
        sim_config["executable_name"] = "bin/champsim"
        sim_config["LLC"]["replacement"] = repl

        json.dump(sim_config, open('my_config.json', 'w'))

        os.system("./config.sh my_config.json")
        os.system("make")

    for i, trace in enumerate(TRACES):
        res_file = f"results/repl/{trace[:-3]}_{repl}.txt"
        if to_run:
            os.system(f"bin/champsim -warmup_instructions {NUM_INSTR} -simulation_instructions {NUM_INSTR} gap_traces/{trace} > {res_file}")

        llc_info = os.popen(f'grep "LLC TOTAL" {res_file}').read().split()
        llc_hit = int(llc_info[5])/int(llc_info[3])

        ipc = os.popen(f'grep "CPU 0 cumulative IPC" {res_file}').read().split()[4]

        out_file.write(f"{trace[:-3]},{repl},{ipc},{llc_hit}\n")
        data[0][i][j] = ipc
        data[1][i][j] = llc_hit
        
ind = np.arange(len(TRACES))
width = 0.1

# print(ind)
# print(data[0])

for i in range(len(TRACES)):
    data[0][i] = data[0][i]/data[0][i][0]
    data[1][i] = data[1][i]/data[1][i][0]

for i in range(len(llc_repl)):
    plt.bar(ind + width*i, data[0][:, i], width, label=llc_repl[i])

plt.xticks(ind+ width*(len(llc_repl) - 1) /2 , TRACES)
plt.legend()
plt.title("Effect on IPC with different LLC replacement policies")
plt.show()

for i in range(len(llc_repl)):
    plt.bar(ind + width*i, data[1][:, i], width, label=llc_repl[i])

plt.xticks(ind + width*(len(llc_repl) - 1) /2 , TRACES)
plt.legend()
plt.title("Effect on hit rate with different LLC replacement policies")
plt.show()



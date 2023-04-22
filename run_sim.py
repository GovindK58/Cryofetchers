import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

to_run = int(sys.argv[1])

NUM_INSTR = 1000000

llc_repl = ["lru", "ship", "srrip"]

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open("results/repl/llc_repl.csv", "w")

data = np.zeros((2, len(llc_repl), len(TRACES)))

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
        data[0][j][i] = ipc
        data[1][j][i] = llc_hit
        
ind = np.arange(len(llc_repl))
width = 0.2

# print(ind)
# print(data[0])

for i in range(len(TRACES)):
    plt.bar(ind + width*i, data[0][:,i], width, label=TRACES[i])

plt.xticks(ind+ width*len(TRACES)/4 , llc_repl)
plt.legend()
plt.title("Effect on IPC with different LLC replacement policies")
plt.show()



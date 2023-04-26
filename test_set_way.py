import json
import os
import matplotlib.pyplot as plt
import numpy as np

llc_sets = [1, 4, 16, 64]
iter = 30000000
# llc_repl = ["lru", "lip", "eaf", "gippr", "random", "fifo", "drrip", "srrip", "ship", "hawkeye", "lfu"]
llc_repl = ["lfu"]

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open("results/llc_set_ways/llc_set_ways.csv", "a")

# data = np.zeros((2, len(llc_sets), len(TRACES)))

for repl in llc_repl:
    sim_config['LLC']['replacement'] = repl
    
    for j, set in enumerate(llc_sets):
        sim_config["executable_name"] = "bin/champsim"
        sim_config["LLC"]["ways"] = sim_config["LLC"]["sets"] * sim_config["LLC"]["ways"] // set
        sim_config["LLC"]["sets"] = set

        json.dump(sim_config, open('my_config.json', 'w'))

        os.system("./config.sh my_config.json")
        os.system("make")
        for i, trace in enumerate(TRACES):
            os.system(f"bin/champsim -warmup_instructions {iter} -simulation_instructions {iter} gap_traces/{trace} > results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt")

            llc_info = os.popen(f'grep "LLC TOTAL" results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt').read().split()
            llc_hit = int(llc_info[5])/int(llc_info[3])

            ipc = os.popen(f'grep "CPU 0 cumulative IPC" results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt').read().split()[4]

            out_file.write(f"{trace[:-3]},{repl},{set},{ipc},{llc_hit}\n")
            # data[0][j][i] = ipc
            # data[1][j][i] = llc_hit
        
# ind = np.arange(len(llc_sets))
# width = 0.2
# for i in range(len(TRACES)):
#     plt.bar(ind + width*i, data[0][:,i], width, label=TRACES[i])

# plt.xticks(ind+ width*len(TRACES)/4 , llc_sets)
# plt.legend()
# plt.title("Effect on IPC with different LLC set,ways")
# plt.show()



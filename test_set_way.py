import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

llc_sets = [1, 4, 16, 64]
iter = 30000000
llc_repl = ["lru", "lip", "eaf", "gippr", "random", "fifo", "drrip", "srrip", "ship", "hawkeye", "lfu"]

to_run = int(sys.argv[1])

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open("results/llc_set_ways/llc_set_ways.csv", "a")

data = np.zeros((2, len(TRACES), len(llc_repl), len(llc_sets)))

for k, repl in enumerate(llc_repl):
    if to_run:
        sim_config['LLC']['replacement'] = repl
    
    for j, set in enumerate(llc_sets):
        if to_run:
            sim_config["executable_name"] = "bin/champsim"
            sim_config["LLC"]["ways"] = sim_config["LLC"]["sets"] * sim_config["LLC"]["ways"] // set
            sim_config["LLC"]["sets"] = set

            json.dump(sim_config, open('my_config.json', 'w'))

            os.system("./config.sh my_config.json")
            os.system("make")
        for i, trace in enumerate(TRACES):
            if to_run:
                os.system(f"bin/champsim -warmup_instructions {iter} -simulation_instructions {iter} gap_traces/{trace} > results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt")

            llc_info = os.popen(f'grep "LLC TOTAL" results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt').read().split()
            llc_hit = int(llc_info[5])/int(llc_info[3])
            ipc = os.popen(f'grep "CPU 0 cumulative IPC" results/llc_set_ways/{trace[:-3]}_{repl}_{set}.txt').read().split()[4]
            # mpki = int(llc_info[7])/int(ipc[6])*1000
            # ipc = ipc[4]

            if to_run:
                out_file.write(f"{trace[:-3]},{repl},{set},{ipc},{llc_hit}\n")
            data[0][i][k][j] = ipc
            data[1][i][k][j] = llc_hit
            # data[2][i][k][j] = mpki
        
ind = np.arange(len(llc_repl))
width = 0.1

# print(ind)
# print(data[0])

for i in range(len(TRACES)):
    data[0][i] = data[0][i]/data[0][i][0][0]
    data[1][i] = data[1][i]/data[1][i][0][0]

    for k in range(len(llc_sets)):
        plt.bar(ind + width*k, data[0][i, :, k], width, label=llc_sets[k])

    plt.xticks(ind+ width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend()
    plt.title("Effect on IPC with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"results/llc_set_ways/pics/{TRACES[i][:-3]}_ipc.png")
    plt.close()

    for k in range(len(llc_sets)):
        plt.bar(ind + width*k, data[1][i, :, k], width, label=llc_sets[k])

    plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    plt.legend()
    plt.title("Effect on hit rate with different LLC replacement policies")
    # plt.show()
    plt.savefig(f"results/llc_set_ways/pics/{TRACES[i][:-3]}_hit.png")
    plt.close()


    # for k in range(len(llc_sets)):
    #     plt.bar(ind + width*k, data[2][i, :, k], width, label=llc_sets[k])

    # plt.xticks(ind + width*(len(llc_repl) - 1) /2 , llc_repl)
    # plt.legend()
    # plt.title("Effect on MPKI with different LLC replacement policies")
    # # plt.show()
    # plt.savefig(f"results/llc_set_ways/pics/{TRACES[i][:-3]}_mpki.png")
    # plt.close()


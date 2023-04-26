#!/usr/bin/python
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import sys

to_run = int(sys.argv[1])

NUM_INSTR = 30000000

sizes = [1024/4, 1024, 4096, 1024*16]
result_dir = "results/l2_size"
# llc_repl = [ ]

sim_config = json.load(open('champsim_config.json'))
TRACES = os.listdir("gap_traces")

out_file = open(f"{result_dir}/l2_size.csv", "a", buffering=10)

data = np.zeros((3, len(TRACES), len(sizes)))

for j, size in enumerate(sizes):
    if to_run:
        sim_config["executable_name"] = "bin/champsim"
        sim_config["L2C"]["sets"] = size

        json.dump(sim_config, open('my_config.json', 'w'))

        os.system("./config.sh my_config.json")
        os.system("make")

        # os.system(f"bin/champsim -warmup_instructions {NUM_INSTR} -simulation_instructions {NUM_INSTR} gap_traces/{TRACES[0]} > {result_dir}/{TRACES[0][:-3]}_lru_l2_{size}.txt & bin/champsim -warmup_instructions {NUM_INSTR} -simulation_instructions {NUM_INSTR} gap_traces/{TRACES[1]} > {result_dir}/{TRACES[1][:-3]}_lru_l2_{size}.txt &")


    for i, trace in enumerate(TRACES):
        res_file = f"{result_dir}/{trace[:-3]}_lru_l2_{size}.txt"
        # if to_run:
        #     os.system(f"bin/champsim -warmup_instructions {NUM_INSTR} -simulation_instructions {NUM_INSTR} gap_traces/{trace} > {res_file}")

        llc_info = os.popen(f'grep "cpu0_L2C TOTAL" {res_file}').read().split()
        ipc = os.popen(f'grep "CPU 0 cumulative IPC" {res_file}').read().split()
        mpki = int(llc_info[7])/int(ipc[6])*1000
        llc_hit = int(llc_info[5])/int(llc_info[3])
        ipc = ipc[4]
        
        out_file.write(f"{trace[:-3]},{size},{ipc},{llc_hit},{mpki}\n")

        data[0][i][j] = ipc
        data[1][i][j] = llc_hit
        data[2][i][j] = mpki
        
ind = np.arange(len(sizes))
width = 0.2

for i in range(len(TRACES)):
    data[0][i] = data[0][i]/data[0][i][1]
    data[1][i] = data[1][i]/data[1][i][1]

plt.figure(figsize=(8, 6))

# for k in range(len(TRACES)):
#     plt.bar(ind + width*k, data[1][k, :], width, label=TRACES[k])sizes = [str(x*8/1024)+"KB" for x in sizes]

sizes = [str(x*8/1024)+"KB" for x in sizes]

plt.bar(sizes, data[0][1, :], 0.4)


# plt.xticks(rotation=45)
plt.xticks(sizes)
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.title(f"Effect on IPC with different L2 sizes on {TRACES[1]}")
plt.subplots_adjust(bottom=0.15, right=0.8)
plt.show()
# plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_ipc.png")
# plt.close()

# plt.figure(figsize=(8, 6))
# for k in range(len(sizes)):
#     plt.bar(ind + width*k, data[1][i, :, k], width, label=sizes[k])

# plt.xticks(rotation=45)
# plt.xticks(ind - 0.8 + width*(len(llc_repl) - 1) /2 , llc_repl)
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
# plt.title("Effect on hit rate with different LLC replacement policies")
# plt.subplots_adjust(bottom=0.15, right=0.8)
# # plt.show()
# plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_hit.png")
# plt.close()

# plt.figure(figsize=(8, 6))
# for k in range(len(sizes)):
#     plt.bar(ind + width*k, data[2][i, :, k], width, label=sizes[k])

# plt.xticks(rotation=45)
# plt.xticks(ind - 0.8 + width*(len(llc_repl) - 1) /2 , llc_repl)

# plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
# plt.title("Effect on MPKI with different LLC replacement policies")
# plt.subplots_adjust(bottom=0.15, right=0.8)
# # plt.show()
# plt.savefig(f"{result_dir}/pics/{TRACES[i][:-3]}_mpki.png")
# plt.close()

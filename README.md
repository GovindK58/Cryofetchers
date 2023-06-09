# Cryofetchers

## By Ankan Sarkar(210050013), Govind Kumar(210050058), Yash Virani(210050170)


The repo contains analysis of different cache hierarchies and cache replacement policies and various insights. \
We are using the latest repo of ChampSim to run simulations. \
We have implemented all the inclusion policies - inclusive, exclusive and non-inclusive. 

All the replacement poicies implemented by us can be found in the replacement folder. They are:
- hawkeye, lip, eaf, lfu, lru, random, drrip, fifo, gippr, srrip, ship

To implement the inclusive and exclusive policy, we made some extra class avriables to account for the data needed in order to implement the policy.

To run a particular simulation with a particular cache inclusion policy use:
```
$ cp <inclusion policy>.cc src/cache.cc
$ ./config.sh <configuration file>
$ make
$ bin/champsim --warmup_instructions 10000000 --simulation_instructions 10000000 <trace_file>
```

We have made several scripts to automate the data generation and plotting
- `run_sim.py`
- `test_l1_size.py`
- `test_l2_size.py`
- `test_set_way.py`; `set_way_plots.py`
- `cache_size.py`; `size_plots.py`

All these above scripts demand a parameter `1` or `0` to denote wheteher to run and plot or only collect the data.

The data generated is stored in the results folder. We are storing the extracted data in csv files. 

## Observations

Our observations are stored in `observations.txt`


The traces used can be downloaded from https://utexas.app.box.com/s/2k54kp8zvrqdfaa8cdhfquvcxwh7yn85/folder/132804598561


References used by us:
- https://seal.ece.ucsb.edu/sites/default/files/publications/hpca-2019-abanti.pdf
- https://core.ac.uk/download/pdf/147122148.pdf


<p align="center">
  <h2 align="center"> ChampSim </h2>
  <p> ChampSim is a trace-based simulator for a microarchitecture study. You can sign up to the public mailing list by sending an empty mail to champsim+subscribe@googlegroups.com. If you have questions about how to use ChampSim, you can often receive a quicker response on the mailing list. Please reserve GitHub Issues for bugs. <p>
</p>

## Using ChampSim

ChampSim is the result of academic research. To support its continued growth, please cite our work when you publish results that use ChampSim by clicking "Cite this Repository" in the sidebar.

## Compile

ChampSim takes a JSON configuration script. Examine `champsim_config.json` for a fully-specified example. All options described in this file are optional and will be replaced with defaults if not specified. The configuration scrip can also be run without input, in which case an empty file is assumed.
```
$ ./config.sh <configuration file>
$ make
```

## Download DPC-3 trace

Traces used for the 3rd Data Prefetching Championship (DPC-3) can be found here. (https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/) A set of traces used for the 2nd Cache Replacement Championship (CRC-2) can be found from this link. (http://bit.ly/2t2nkUj)

Storage for these traces is kindly provided by Daniel Jimenez (Texas A&M University) and Mike Ferdman (Stony Brook University). If you find yourself frequently using ChampSim, it is highly encouraged that you maintain your own repository of traces, in case the links ever break.

## Run simulation

Execute the binary directly.
```
$ bin/champsim --warmup_instructions 200000000 --simulation_instructions 500000000 ~/path/to/traces/600.perlbench_s-210B.champsimtrace.xz
```

The number of warmup and simulation instructions given will be the number of instructions retired. Note that the statistics printed at the end of the simulation include only the simulation phase.

## Add your own branch predictor, data prefetchers, and replacement policy
**Copy an empty template**
```
$ mkdir prefetcher/mypref
$ cp prefetcher/no_l2c/no.cc prefetcher/mypref/mypref.cc
```

**Work on your algorithms with your favorite text editor**
```
$ vim prefetcher/mypref/mypref.cc
```

**Compile and test**
Add your prefetcher to the configuration file.
```
{
    "L2C": {
        "prefetcher": "mypref"
    }
}
```
Note that the example prefetcher is an L2 prefetcher. You might design a prefetcher for a different level.

```
$ ./config.sh <configuration file>
$ make
$ bin/champsim --warmup_instructions 200000000 --simulation_instructions 500000000 600.perlbench_s-210B.champsimtrace.xz
```

## How to create traces

Program traces are available in a variety of locations, however, many ChampSim users wish to trace their own programs for research purposes.
Example tracing utilities are provided in the `tracer/` directory.

## Evaluate Simulation

ChampSim measures the IPC (Instruction Per Cycle) value as a performance metric. <br>
There are some other useful metrics printed out at the end of simulation. <br>

Good luck and be a champion! <br>

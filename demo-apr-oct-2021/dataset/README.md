# Graphs

This folder contains measurement data about CPU and memory usage extracted using the [sysstat](https://github.com/sysstat/sysstat) tool, setting the measurement interval to 1 minute, in the [data](./data) folder. The folder also contains measurements interval extracted using bash scripts in the [scripts](./scripts) folder.

To generate the graphs:
```bash
# create a virtual environment
python3 -m venv .venv
# activate the virtual environment
source .venv/bin/activate
# install dependencies with pip
pip install pandas matplotlib
# generate graphs about resource consumption
python resource_usage.py
# generate graphs about reaction times
python reaction_times.py
# print deltas about CPU and memory usage
python deltas.py
```
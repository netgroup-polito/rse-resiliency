import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pprint

class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


setups = ["arm64","x64"]

filepath = "./data/"

imagepath = "./images/"

memory_size_in_GB = 4

n_core = 4  # used to normalize data for calculating equivalent cpu usage in one core, for then get vCPU usage

fontsize = 13

plt.rc('font', size=fontsize) #controls default text size
plt.rc('axes', titlesize=fontsize +2 ) #fontsize of the title
plt.rc('axes', labelsize=fontsize) #fontsize of the x and y labels
plt.rc('xtick', labelsize=fontsize) #fontsize of the x tick labels
plt.rc('ytick', labelsize=fontsize) #fontsize of the y tick labels
plt.rc('legend', fontsize=fontsize) #fontsize of the legend

def get_means():

    global memory_size_in_GB
    global pdc_base

    measurements = {
        "ubuntu-vanilla": "linux vanilla",
        "docker": "linux + docker",
        "mysql-docker": "mysql (container)",
        "mysql-vanilla": "mysql",
        "openpdc-alpine-docker": "pdc\n(alpine)",
        "openpdc-ubuntu-docker": "pdc\n(ubuntu)",
        "openpdc-vanilla": "pdc",
        "pmu-docker" : "pmu (container)",
        "pmu-vanilla": "pmu",
        "normal-deploy-alpine": "normal deployment",
        "normal-deploy-ubuntu": "normal deployment",
        "whole-deploy-alpine": "whole deployment",
        "whole-deploy-ubuntu": "whole deployment",
        "k3s-master": "k3s master",
        "k3s-worker": "k3s worker",
        "k3s-master-lh": "k3s master\n+ longhorn",
        "k3s-worker-lh": "k3s worker\n+ longhorn"
    }

    delta_cpu = {
        "arm64": {},
        "x64": {}
    }

    delta_memory = {
        "arm64": {},
        "x64": {}
    }

    for arch in setups:
        print(f"{bcolors.WARNING}-----{arch}-----{bcolors.RESET}")
        data_cpu = dict()
        data_memory = dict()

        if not os.path.exists(f"{imagepath}/{arch}"):
            os.makedirs(f"{imagepath}/{arch}")

        memory_size_in_GB = 4 if arch == "arm64" else 8

        pdc_base = "alpine" if arch == "arm64" else "ubuntu"

        missing = []

        for m, col_name in measurements.items():
            if os.path.exists(filepath + f"{arch}/{m}/cpu.csv") and os.path.exists(filepath + f"{arch}/{m}/memory.csv"):
                data_cpu[m] = getCPUDataFromFile(filepath + f"{arch}/{m}/cpu.csv", col_name)[col_name].mean()
                data_memory[m] = getMemoryDataFromFile(filepath + f"{arch}/{m}/memory.csv", col_name)[col_name].mean()
                print(f"{bcolors.OK}{m}{bcolors.RESET}")
                print("cpu mean:", data_cpu[m])
                print("memory mean:", data_memory[m])
            else:
                missing.append(m)
                print(f"skipping {m} on {arch}")

        delta_cpu[arch]["pdc-ubuntu"] = data_cpu["openpdc-ubuntu-docker"] - data_cpu["openpdc-vanilla"]
        delta_cpu[arch]["pdc-alpine"] = data_cpu["openpdc-alpine-docker"] - data_cpu["openpdc-vanilla"]
        delta_cpu[arch]["pmu-alpine"] = data_cpu["pmu-docker"] - data_cpu["pmu-vanilla"]
        delta_cpu[arch]["mysql-docker"] = data_cpu["mysql-docker"] - data_cpu["mysql-vanilla"]
        delta_cpu[arch]["k3s-master"] = n_core * (data_cpu["k3s-master"] - data_cpu["ubuntu-vanilla"] )
        delta_cpu[arch]["k3s-worker"] = n_core * ( data_cpu["k3s-worker"] - data_cpu["ubuntu-vanilla"])
        delta_cpu[arch]["k3s-master-longhorn"] = n_core * (data_cpu["k3s-master-lh"] - data_cpu["ubuntu-vanilla"])
        delta_cpu[arch]["k3s-worker-longhorn"] = n_core * (data_cpu["k3s-worker-lh"] - data_cpu["ubuntu-vanilla"] )



        delta_memory[arch]["pdc-ubuntu"] = data_memory["openpdc-ubuntu-docker"] - data_memory["openpdc-vanilla"]
        delta_memory[arch]["pdc-alpine"] = data_memory["openpdc-alpine-docker"] - data_memory["openpdc-vanilla"]
        delta_memory[arch]["pmu-alpine"] = data_memory["pmu-docker"] - data_memory["pmu-vanilla"]   
        delta_memory[arch]["mysql-docker"] = data_memory["mysql-docker"] - data_memory["mysql-vanilla"]
        delta_memory[arch]["k3s-master"] = data_memory["k3s-master"] - data_memory["ubuntu-vanilla"]
        delta_memory[arch]["k3s-worker"] = data_memory["k3s-worker"] - data_memory["ubuntu-vanilla"]
        delta_memory[arch]["k3s-master-longhorn"] =  data_memory["k3s-master-lh"] - data_memory["ubuntu-vanilla"]
        delta_memory[arch]["k3s-worker-longhorn"] = data_memory["k3s-worker-lh"] - data_memory["ubuntu-vanilla"]

    print(f"{bcolors.OK}CPU{bcolors.RESET}")    
    pprint.pprint(delta_cpu)
    print(f"{bcolors.OK}Memory{bcolors.RESET}")  
    pprint.pprint(delta_memory)



def getCPUDataFromFile(path: str, col_name: str) -> pd.DataFrame:
    data = pd.read_csv(path, header=0, converters={"timestamp": pd.Timestamp}, sep=";")
    return (100 - data.loc[:, ["%idle[...]"]]).rename({"%idle[...]": col_name}, axis=1)

def getMemoryDataFromFile(path: str, col_name: str) ->pd.DataFrame:
    data = pd.read_csv(path, header=0, converters={"timestamp": pd.Timestamp}, sep=";")
    return (memory_size_in_GB/100 * data.loc[:, ["%memused"]]).rename({"%memused": col_name}, axis=1)

if __name__ == "__main__":
   get_means()
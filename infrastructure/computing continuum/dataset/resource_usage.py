import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

setups = ["arm64","x64"]

filepath = "./data/"

imagepath = "./images/"

memory_size_in_GB = 4

fontsize = 13

plt.rc('font', size=fontsize) #controls default text size
plt.rc('axes', titlesize=fontsize +2 ) #fontsize of the title
plt.rc('axes', labelsize=fontsize) #fontsize of the x and y labels
plt.rc('xtick', labelsize=fontsize) #fontsize of the x tick labels
plt.rc('ytick', labelsize=fontsize) #fontsize of the y tick labels
plt.rc('legend', fontsize=fontsize) #fontsize of the legend

def graph():
    global memory_size_in_GB

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
        "k3s-worker-lh": "k3s worker\n+ longhorn",
        "master-1": "master\nnode 1",
        "master-2": "master\nnode 2",
        "master-3": "master\nnode 3",
        "worker": "worker\nnode"
    }

    for arch in setups:
        data_cpu = dict()
        data_memory = dict()

        if not os.path.exists(f"{imagepath}/{arch}"):
            os.makedirs(f"{imagepath}/{arch}")

        memory_size_in_GB = 4 if arch == "arm64" else 8

        pdc_base = "alpine" if arch == "arm64" else "ubuntu"

        graphs = {
            "containerized apps": {
                "sources": ["ubuntu-vanilla", "docker", "mysql-docker", f"openpdc-{pdc_base}-docker","pmu-docker", f"normal-deploy-{pdc_base}", f"whole-deploy-{pdc_base}"],
                "titles": {
                    "cpu": "CPU impact of containerized apps",
                    "memory": "Memory impact of containerized apps",
                },
                "label_rotation": 30,
                "subplot_adjust": {
                    "bottom" : 0.3,
                    "top": 0.9
                }
            },
            "pdc comparison": {
                "sources": ["ubuntu-vanilla", "openpdc-vanilla" ,"openpdc-alpine-docker","openpdc-ubuntu-docker" ],
                "titles": {
                    "cpu": "CPU usage comparison for OpenPDC",
                    "memory": "Memory usage comparison for OpenPDC",
                },
            },
            "vanilla app comparison": {
                "sources": ["ubuntu-vanilla", "openpdc-vanilla" ,f"openpdc-{pdc_base}-docker", "pmu-vanilla", "pmu-docker", "mysql-vanilla", "mysql-docker" ],
                "titles": {
                    "cpu": "CPU usage apps vs containerized apps",
                    "memory": "Memory usage apps vs containerized apps",
                },
                "label_rotation": 30,
                "subplot_adjust": {
                    "bottom" : 0.25,
                    "top": 0.9
                }
            },
            "k3s comparison": {
                "sources": ["k3s-master","k3s-worker","k3s-master-lh","k3s-worker-lh"],
                "titles": {
                    "cpu": "k3s CPU usage",
                    "memory": "k3s memory usage",
                },
                "subplot_adjust": {
                    "bottom" : 0.1,
                    "top": 0.9
                }
            },
            "demo": {
                "sources": ["master-1","master-2","master-3","worker"],
                "titles": {
                    "cpu": "Demo deployment - CPU",
                    "memory": "Demo deployment - memory",
                },
                "subplot_adjust": {
                    "bottom" : 0.1,
                    "top": 0.9
                }
            },
        }

        missing = []

        for m, col_name in measurements.items():
            if os.path.exists(filepath + f"{arch}/{m}/cpu.csv") and os.path.exists(filepath + f"{arch}/{m}/memory.csv"):
                if (m in graphs["demo"]["sources"] and arch == "arm64") or (arch == "x64"):
                    memory_size_in_GB = 8
                else:
                    memory_size_in_GB = 4
                data_cpu[m] = getCPUDataFromFile(filepath + f"{arch}/{m}/cpu.csv", col_name)
                data_memory[m] = getMemoryDataFromFile(filepath + f"{arch}/{m}/memory.csv", col_name)
            else:
                missing.append(m)
                print(f"skipping {m} on {arch}")

        for key, settings in graphs.items():
            if any(item in settings["sources"] for item in missing):
                print(f"skipping graph {key} on {arch}")
            else:
                cpu = pd.concat([data_cpu[i] for i in settings["sources"]], axis=1)
                createFigure(cpu, settings, settings["titles"]["cpu"], "CPU consumption [%]", arch)
                memory = pd.concat([data_memory[i] for i in settings["sources"]], axis=1)
                createFigure(memory, settings, settings["titles"]["memory"], "Memory consumption [GB]", arch)


def getCPUDataFromFile(path: str, col_name: str):
    data = pd.read_csv(path, header=0, converters={"timestamp": pd.Timestamp}, sep=";")
    return (100 - data.loc[:, ["%idle[...]"]]).rename({"%idle[...]": col_name}, axis=1)

def getMemoryDataFromFile(path: str, col_name: str):
    data = pd.read_csv(path, header=0, converters={"timestamp": pd.Timestamp}, sep=";")
    return (memory_size_in_GB/100 * data.loc[:, ["%memused"]]).rename({"%memused": col_name}, axis=1)

def createFigure(data: pd.DataFrame, settings: dict, title: str, ylabel: str, arch: str):
    plt.close('all')

    plot = data.plot.box()

    if "subplot_adjust" in settings.keys():
        plot.figure.subplots_adjust(
            bottom=settings["subplot_adjust"]["bottom"],
            top=settings["subplot_adjust"]["top"])

    if "label_rotation" in settings.keys():
        plt.setp(plot.get_xticklabels(), rotation=settings["label_rotation"], horizontalalignment='right')

    plot.set_title(title + f" on {arch}")

    plot.set_ylabel(ylabel)

    plot.grid(settings.get("grid", True))

    filename = title.replace(" ", "_").lower()

    plot.get_figure().savefig(f"{imagepath}{arch}/{filename}.pdf")
    

if __name__ == "__main__":
   graph()
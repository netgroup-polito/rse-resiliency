import pandas as pd
import matplotlib.pyplot as plt
import os

filepath = "./data_seba/"

imagepath = "./data_seba/images/"

if not os.path.exists(imagepath):
    os.makedirs(imagepath)

reaction = pd.read_csv(
        f"{filepath}reaction_times_delete_pod.log", 
        header=0
        )

intervals = []

for index, row in reaction.iterrows():
    if index in [0,1]: #skip header
        continue
    intervals.append(row["restart_time"]/1000) #append in seconds

df = pd.DataFrame(intervals)

plot = df.plot.box()

plot.set_title('PMU pod restart time')

plot.set_ylabel('sec')

plot.get_figure().savefig(imagepath + "reactions-restart-pod-pmu.pdf")

plt.close('all')
     
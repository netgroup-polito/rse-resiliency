import pandas as pd
import matplotlib.pyplot as plt
import os

filepath = "./data_seba/"

imagepath = "./data_seba/images/"

if not os.path.exists(imagepath):
    os.makedirs(imagepath)

reaction = pd.read_csv(
        f"{filepath}restart_send_data_after_delete.log", 
        header=0
        )

intervals = []

for index, row in reaction.iterrows():
    if index in [0,1]: #skip header
        continue
    intervals.append(row["restart_send"]/1000) #append in seconds

df = pd.DataFrame(intervals)

plot = df.plot.box()

plot.set_title('PMU pod restarts to send data after "kubectl delete pod"')

plot.set_ylabel('sec')

plot.get_figure().savefig(imagepath + "pmu-restart-send-after-delete.pdf")

plt.close('all')
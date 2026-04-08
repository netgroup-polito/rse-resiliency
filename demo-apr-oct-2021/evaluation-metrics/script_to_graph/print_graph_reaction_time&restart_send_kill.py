import pandas as pd
import matplotlib.pyplot as plt
import os

filepath = "./data_seba/"

imagepath = "./data_seba/images/"

if not os.path.exists(imagepath):
    os.makedirs(imagepath)

reaction = pd.read_csv(
        f"{filepath}restart_send_data_after_kill.log", 
        header=0
        )

intervals_restart = []
intervals_restart_send = []
deltas = []

for index, row in reaction.iterrows():
    if index in [0,1]: #skip header
        continue
    intervals_restart.append(row["restart_time"]) #append in seconds
    intervals_restart_send.append(row["restart_sends"]) #append in seconds
    deltas.append(row["restart_sends"] - row["restart_time"])

#my_dict = {'time_restart_pod': intervals_restart, 'time_resends_data': intervals_restart_send}


df = pd.DataFrame(intervals_restart)
plot = df.plot.box()
plot.set_title('PMU pod restart time')
plot.set_ylabel('sec')
plot.get_figure().savefig(imagepath + "pmu-restart-after-kill.pdf")
plt.close('all')

df = pd.DataFrame(intervals_restart_send)
plot = df.plot.box()
plot.set_title('PMU pod restarts to send data after "kill process"')
plot.set_ylabel('sec')
plot.get_figure().savefig(imagepath + "pmu-restart-send-data-after-kill.pdf")
plt.close('all')

# fig, ax = plt.subplots()
# ax.boxplot(my_dict.values())
# ax.set_xticklabels(my_dict.keys())
# ax.set_title('Time to restart a PMU and Time to resend Data after Kill Process')
# ax.get_figure().savefig(f"{imagepath}pmu-restart-and-restart-send-after-kill.pdf")

#Plot deltas
df = pd.DataFrame(deltas)
plot = df.plot.box()
plot.set_title('Delta time from when the PMU is running to when it actually sends data')
plot.set_ylabel('sec')
plot.get_figure().savefig(imagepath + "deltas.pdf")
plt.close('all')



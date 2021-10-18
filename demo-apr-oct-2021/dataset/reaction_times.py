import pandas as pd
import matplotlib.pyplot as plt
import os

filepath = "./data/"

imagepath = "./images/"

if not os.path.exists(imagepath):
    os.makedirs(imagepath)

reaction = pd.read_csv(
    f"{filepath}reactions/reactions.csv", 
    header=0,
    sep=";"
    )

data = pd.concat([reaction.loc[:, "not ready interval"], reaction.loc[:, "recreation interval"], reaction.loc[:, "sum"]], axis=1)

plot = data.plot.box()

plot.set_title('Kubernetes reaction times to node fault')

plot.set_ylabel('sec')

plot.get_figure().savefig(f"{imagepath}reactions-node-failure.pdf")

plt.close('all')

for i in range(1,7):
    reaction = pd.read_csv(
        f"{filepath}container-restart/log{i}.log", 
        header=0
        )
    
    prev_down = 0
    intervals = []

    for index, row in reaction.iterrows():
        if index in [0,1]:
            continue
        if row["status"] == "down":
            prev_down = row["timestamp"]
        else:
            i = row["timestamp"] - prev_down
            intervals.append(i)

    intervals_in_s = [x / 1000000000 for x in intervals]
    print(intervals_in_s)

df = pd.DataFrame( # data taken and cleared from the above prints
    {"restart time": [1.02397386, 2.045213952, 1.023102982, 2.190487426, 1.023692706, 2.289065071, 1.025222069, 2.24045543]})

plot = df.plot.box()

plot.set_title('Kubernetes container restart time')

plot.set_ylabel('sec')

plot.get_figure().savefig(imagepath + "reactions-restart-container.pdf")

plt.close('all')

# reaction times

reaction = pd.read_csv(
    f"{filepath}reactions/log", 
    header=0
    )

#reaction["timestamp"] = reaction["timestamp"].apply(lambda x: x / 1000000)

prev_down = 0
intervals = []

for index, row in reaction.iterrows():
    if index in [0,1]:
        continue
    if row["status"] == "down":
        prev_down = row["timestamp"]
    else:
        i = row["timestamp"] - prev_down
        intervals.append(i)

intervals_in_s = [x / 1000000000 for x in intervals]

retries = range(len(intervals))

cleaned_intervals = []

for i in intervals_in_s:
    if i > 10 and i < 20:
        cleaned_intervals.append(i - 10)
    elif i > 20 and i < 40:
        cleaned_intervals.append(i - 20)
    elif i > 40 and i < 80:
        cleaned_intervals.append(i - 40)
    elif i > 80 and i < 160:
        cleaned_intervals.append(i - 80)
    elif i > 160 and i < 300:
        cleaned_intervals.append(i - 160)
    elif i > 300:
        cleaned_intervals.append(i - 300)
    else:
        cleaned_intervals.append(i)

data = pd.DataFrame(cleaned_intervals)

fig, ax = plt.subplots()

ax.plot(retries, intervals_in_s)

plt.show()

ax.set_ylabel('restart interval [sec]')

ax.set_xlabel('Retries')

ax.set_title('Nginx container restart time in case of failure')

ax.get_figure().savefig(f"{imagepath}reactions.pdf")

plt.close('all')
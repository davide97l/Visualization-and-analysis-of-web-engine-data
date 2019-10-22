import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import datetime as dt


csv_files = glob.glob("data/*.csv")
csv_dataset = []
for n, filename in enumerate(csv_files):
    print("Elaborating file {}".format(n+1))
    df = pd.read_csv(filename)
    csv_dataset.append(df)
dataset = pd.concat(csv_dataset, axis=0, ignore_index=True)


# only to test on a smaller dataset
#dataset_path = "data/data.csv"
#dataset = pd.read_csv(dataset_path)

srt = dataset["SRT"]
n_images = dataset["#Images"]
province = dataset["Province"]
ua = dataset["UA"]
tmstmp = dataset["Timestamp"]

# 1) Calculate the average SRT of every 10 minutes, and plot the SRT with a line chart (x axis for date time and y axis
# for the average SRT).
srt_tmstmp = {}
srt_count = {}
unit_time = 600  # ten minutes
for index, row in dataset.iterrows():
    key = (row["Timestamp"])//unit_time
    new_item = [row["SRT"], row["Tnet"], row["Tserver"], row["Tbrowser"], row["Tother"]]
    if srt_tmstmp.get(key) is not None:
        srt_tmstmp[key] = [sum(i) for i in zip(srt_tmstmp[key], new_item)]
    else:
        srt_tmstmp[key] = new_item
        srt_count[key] = 1
    srt_count[key] += 1
for key in srt_tmstmp.keys():
    srt_tmstmp[key] = [x / srt_count[key] for x in srt_tmstmp[key]]
avg_srt = np.array(list(srt_tmstmp.values()))[:, 0]
y1 = np.array(list(srt_tmstmp.values()))[:, 1]
y2 = np.array(list(srt_tmstmp.values()))[:, 2]
y3 = np.array(list(srt_tmstmp.values()))[:, 3]
y4 = np.array(list(srt_tmstmp.values()))[:, 4]
fig, ax = plt.subplots()
ax.grid(True)

t_dates = np.array(list(srt_tmstmp.keys()))
dates = [dt.datetime.fromtimestamp(int(ts) * unit_time) for ts in t_dates]
ax.plot(dates, list(avg_srt))
ax.get_xaxis().set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=2, tz=None))
ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%b %d'))

ax.set_title('Average SRT of every 10 minutes')
ax.set_ylabel('Average SRT (ms)')
plt.savefig("fig1")

# 2) Calculate the average of each SRT component of every 10 minute, and plot the four SRT components together with a
# stacked area chart (x axis for date time and y axis for time) and also a 100% stacked area chart (y axis for the
# percentage).
labels = ["Tnet", "Tserver", "Tbrowser", "Tother"]
fig, ax = plt.subplots()

ax.stackplot(dates, y1, y2, y3, y4, labels=labels)
ax.get_xaxis().set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=2, tz=None))
ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%b %d'))

ax.grid(True)
ax.legend(loc='upper left')
ax.set_title('Average SRT components of every 10 minutes')
ax.set_ylabel('Average SRT components (ms)')
plt.savefig("fig2")

fig, ax = plt.subplots()
ax.stackplot(dates, y1/avg_srt*100, y2/avg_srt*100, y3/avg_srt*100, y4/avg_srt*100, labels=labels)
ax.get_xaxis().set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=2, tz=None))
ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%b %d'))
ax.grid(True)
ax.legend(loc='upper left')
ax.set_title('Average SRT components of every 10 minutes (%)')
ax.set_ylabel('Average SRT components (%)')
plt.savefig("fig3")

# 3) Plot the CDF (Cumulative distribution function) chart of SRT.
fig, ax = plt.subplots()
n, bins, patches = ax.hist(srt, bins=int(max(srt)), density=True, histtype='stepfilled', cumulative=True)
ax.grid(True)
ax.set_title('CDF chart of SRT')
ax.set_xlabel('SRT (ms)')
ax.set_ylabel('Probability')
plt.savefig("fig4")

# 4) Plot the CDF chart of #Images.
fig, ax = plt.subplots()
n, bins, patches = ax.hist(n_images, bins=max(n_images), density=True, histtype='stepfilled', cumulative=True)
ax.grid(True)
ax.set_title('CDF chart of number of images')
ax.set_xlabel('Images')
ax.set_ylabel('Probability')
plt.savefig("fig5")

# 5) Count the number of queries (also called page views or PVs) of each minute, and plot the minute-level PVs with a
# line chart (x axis for date time and y axis for the PVs).
query_min = {}
unit_time = 60  # 1 minute
for index, row in dataset.iterrows():
    key = (row["Timestamp"])//unit_time
    if query_min.get(key) is not None:
        query_min[key] += 1
    else:
        query_min[key] = 1

fig, ax = plt.subplots()
t_dates = np.array(list(query_min.keys()))
dates = [dt.datetime.fromtimestamp(int(ts) * unit_time) for ts in t_dates]
ax.plot(dates, list(query_min.values()))
ax.get_xaxis().set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=2, tz=None))
ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%b %d'))
ax.grid(True)
ax.set_title('PVs per minute')
ax.set_ylabel('PVs')
plt.savefig("fig6")

# 6) Count the PVs of each province, and plot it with a histogram chart (x axis for province and y axis for PVs).
fig, ax = plt.subplots()
n, bins, patches = ax.hist(province, bins=len(province), histtype='bar', align='mid', width=0.8)
ax.set_title('PVs of each province')
ax.set_ylabel('PVs')
plt.xticks(rotation=45)
plt.savefig("fig7")

# 7) Count the PVs of each UA, and plot it with a pie chart (show the percentages in the chart).
pvs_ua = ua.value_counts().to_numpy()
unique_ua = (dataset.UA.unique())
fig, ax = plt.subplots()


def autopct(pct):
    return ('%1.1f' % pct) if pct >= 3 else ''


n, bins, patches = ax.pie(pvs_ua, labels=unique_ua, autopct=autopct, shadow=True, startangle=90, labeldistance=None)
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax.set_title('PVs of each UA')
ax.legend(loc='upper left')
plt.savefig("fig8")


plt.show()

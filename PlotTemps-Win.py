#!/usr/bin/env python3

import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import csv
import string

remotehost = "pi1"
remotefile = "timeseries.csv"
localfile = "D:\\Users\\nick\\workspace\\HomeAutomation\\poolcontrol\\timeseries"+ datetime.datetime.now().strftime("%y%m%d") + ".csv" 

print(os.system('scp %s:%s %s' % (remotehost, remotefile, localfile)))

pool = []
roof = []
pumpNeed = []
pumpState = []
time = []


with open( localfile, 'r', encoding='utf-8',errors='ignore') as csvfile:
    plots = csv.reader((line.replace('\0','') for line in csvfile), delimiter=",")
    next(plots, None)
    for row in plots:
        time.append(mdate.epoch2num(int(row[0])))
        roof.append(float(row[1]))
        pool.append(float(row[2]))
        pumpNeed.append(20 + int(row[3])*10)
        pumpState.append(20 + int(row[4])*10)
      


plt.plot_date(time, roof,'', tz="Australia/Melbourne")
plt.plot_date(time, pool,'', tz="Australia/Melbourne")
plt.plot_date(time, pumpNeed,'',tz="Australia/Melbourne")
plt.plot_date(time, pumpState,'',tz="Australia/Melbourne")
plt.show()

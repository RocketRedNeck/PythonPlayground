# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 14:31:00 2016

@author: mtkessel
"""

import matplotlib.pyplot as plt
from numpy.random import random, randint
import pandas as pd

dates = [
1665,
1674,
1838,
1839,
1855]

values = [1,2,3,4,5]

X = dates #pd.to_datetime(dates)
fig, ax = plt.subplots(figsize=(6,1))
ax.scatter(X, [1]*len(X), c=values,
           marker='s', s=100)
fig.autofmt_xdate()

# everything after this is turning off stuff that's plotted by default

ax.yaxis.set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.xaxis.set_ticks_position('bottom')

ax.get_yaxis().set_ticklabels([])
day = 10 #pd.to_timedelta("1", unit='D')
plt.xlim(X[0] - day, X[-1] + day)
plt.show()

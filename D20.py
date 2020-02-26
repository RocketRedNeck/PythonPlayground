# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 08:00:13 2018

@author: mtkes
"""

import numpy as np
from matplotlib import pyplot as pl
import time

np.random.seed(int(np.round(time.time())))

N = 100000

die1 = np.random.randint(1,21,N)
die2 = np.random.randint(1,21,N)

pl.figure(1)
pl.hist(die1,50)
pl.grid()

pl.figure(2)
pl.hist(die2,50)
pl.grid()

avg_die1 = np.average(die1)
print("Die 1 = ", avg_die1)

avg_die2 = np.average(die2)
print("Die 2 = ", avg_die2)

diePair = [die1,die2]

maxDie = np.max(diePair,0)
pl.figure(3)
pl.hist(maxDie,50)
pl.grid()

minDie = np.min(diePair,0)
pl.figure(4)
pl.hist(minDie,50)
pl.grid()
pl.show()

avg_min = np.average(minDie)
print("Minimum = ", avg_min)

avg_max = np.average(maxDie)
print("Maximum = ", avg_max)


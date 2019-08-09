# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 20:51:04 2017

@author: mtkes
"""
import matplotlib.pyplot as pl
import numpy as np


R = np.arange(1.1, 4, 0.01)
x = np.zeros((R.size, 1000))
x[:,0] = 0.5

j = 0
for r in R:
    for i in range(999):
        x[j,i+1] = r * x[j,i] * (1 - x[j,i])
    j += 1
    
pl.figure(1)
pl.plot(R,x[:,499:999])

pl.figure(2)
pl.hist(x[R.size-1,499:999],100)

pl.show()
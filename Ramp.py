# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as pl
import numpy as np

l = 40
w = 150
X = np.arange(0.25*l, 0.75*l)

m = X * w

pl.figure(1)
pl.plot(X,m)
pl.xlabel('Robot CM Position (inch from hinge)')
pl.ylabel('Hinge Moment (ft lbf)')
pl.grid()

f = np.zeros(X.size)
f = w * X / (2*(2*X-l))

        
pl.figure(2)
pl.plot(X,f)
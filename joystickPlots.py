# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as pl
import numpy as np

x = np.arange(-127,127,1) / 127

y1 = x
y2 = np.sign(x)*(x ** 2)
y3 = x ** 3
y4 = np.sign(x)*(np.log(1-abs(x))) / np.log(1/127)
y5 = np.abs(x)*np.sin(x*np.pi/2)

pl.plot(x,y1,x,y2,x,y3,x,y4,x,y5)
pl.grid()
pl.legend(['x', 'x**2','x**3','log','sin'],loc="upper left")


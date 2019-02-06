# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as pl
import numpy as np

x = np.arange(-127,127,1) / 127

y1 = np.array(x)
y2 = abs(x)*x
y3 = x ** 3
y4 = np.sign(x)*(np.log(1-abs(x))) / np.log(1/127)
y5 = np.abs(x)*np.sin(x*np.pi/2)

pl.figure(1)
pl.plot(x,y1,x,y2,x,y3,x,y5)
pl.xlabel('Input Value')
pl.ylabel('Output Value')
pl.grid()
pl.legend(['x', '|x|*x','x**3','sine'],loc="upper left")
pl.savefig("Figure1.png")

pl.figure(2)
db = 0.15
idx = np.where(np.abs(x) < db)
idx2 = np.where(x >= db)
idx3 = np.where(x <= -db)
yy = np.array(y1)
yy[idx] = 0.0;
yy[idx2] = (yy[idx2]-db)/(1.0-db)
yy[idx3] = (yy[idx3]+db)/(1.0-db)
pl.plot(x,y1,x,yy)
pl.xlabel('Input Value')
pl.ylabel('Output Value')
pl.grid()
pl.legend(['f(x) = x','f(x) = pieces'],loc="upper left")
pl.savefig("Figure12.png")


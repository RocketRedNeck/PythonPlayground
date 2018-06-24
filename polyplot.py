# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 20:52:08 2018

@author: mtkes
"""
import matplotlib.pyplot as pl
import numpy as np


from scipy.interpolate import spline

#Input the y coordinate of point 1 10
#Input the x coordinate of point 2 30
#Input the y coordinate of point 2 40
#Input the x coordinate of point 3 65
#Input the y coordinate of point 3 65
#Input the x coordinate of point 4 100
#Input the y coordinate of point 4 100
# 2.040816326530693E-4 -0.03571428571428703 2.663265306122489 -13.265306122449259 

x = np.array([10, 10, 40, 60])
y = np.array([10, 40, 40, 60])
xxx = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,13,14,15,16,17,16,15,14])
yyy = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,20])

xnew = np.linspace(xxx.min(),xxx.max(),100) #300 represents number of points to make between T.min and T.max

yyy_smooth = spline(xxx,yyy,xnew)




bly = np.array([13,13,13,14,15])
blx = np.array([21,20,19,19,19])

xx = np.arange(10,100,0.05)
yy = (2.040816326530693E-4 * xx**3) + (-0.03571428571428703 * xx**2) + (2.663265306122489 * xx) + (-13.265306122449259)

pl.ylim((0,25))
pl.xlim((0,25))
pl.axis('equal')
#pl.set_xticks(np.arange(0, 25, 1),minor=True)
pl.grid(which='both')
pl.plot(0.5,0.5,'o',bly,blx,'r',xxx+0.5,yyy+0.5,xnew,yyy_smooth)


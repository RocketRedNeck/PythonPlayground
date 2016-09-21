# -*- coding: utf-8 -*-
"""
tau demonstrates plotting of time constant with numpy and matplotlib
"""

import matplotlib.pyplot as plot
import numpy as np

t = np.arange(0.0, 1.0, 0.01)   # start, stop, step

def f(t, tau, delay):
    """
    t is an array of time
    tau is a scalar
    delay is a scalar
    """
    f = 1-np.exp(-(t-delay)/tau)
    f[np.where(f < 0.0)] = 0.0
    return f
    
plot.figure(1)
plot.cla()
taus = np.arange(0.01,1.0,0.01)
for tau in taus:
    plot.plot(t,f(t,tau, 0.2))



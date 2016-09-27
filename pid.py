# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 21:57:29 2016

@author: mtkes
"""

import matplotlib.pyplot as plot
import numpy as np

tmax = 1000
ts = np.arange(0, tmax, 1)
pvs = np.zeros(tmax)


kp = 0.2
ki = 0.01
kd = 0.0  

dt = ts[1] - ts[0]

Gp = 2
delay = 50 * dt
tau = 10 * dt
 

sp  = 1.0
err = 0.0
intErr = 0.0
lastErr = 0.0
lastT = ts[0]

lastG = 0.0

i = 0
d = 0
exp = -np.exp(-1/tau)
for t in ts:
    derr = err - lastErr
    intErr = intErr + err
    mv = (kp * err) + (ki * intErr) + (kd * (derr/dt))
    G = 0.0
    if (t >= delay):
        G = mv * Gp * (1.0 + exp) - (lastG * exp)
    else:
        d += 1
    
    pvs[i] = G
    lastG = G

    i += 1
    
    lastErr = err
    err = 0.0
    if (t >= delay):
        err = sp - pvs[i-d]
        
    #err += np.random.randn(1)*0.04
    
    
plot.figure(1)
plot.cla()
plot.grid()
plot.plot(ts,pvs)
    
    
    
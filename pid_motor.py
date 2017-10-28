# -*- coding: utf-8 -*-
"""
pid - example of PID control of a simple process with a time constant

Copyright (c) 2016 - RocketRedNeck.com RocketRedNeck.net 

RocketRedNeck and MIT Licenses 

RocketRedNeck hereby grants license for others to copy and modify this source code for 
whatever purpose other's deem worthy as long as RocketRedNeck is given credit where 
where credit is due and you leave RocketRedNeck out of it for all other nefarious purposes. 

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions: 

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software. 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE. 
"""

import matplotlib.pyplot as plot
import numpy as np
import math

tmax = 3.0
dt = 0.01
ts = np.arange(0.0, tmax, dt)
pvs = np.zeros(len(ts))
sps = np.zeros(len(ts))
mvs = np.zeros(len(ts))
mps = np.zeros(len(ts))


kf = 0.0
kp = 20.0
ki = 0.0
kd = 0.0  

dt = ts[1] - ts[0]

Gp = 1
delay = 1 * dt
tau = 10000 * dt
 

sp_period  = 1.0

err = 0.0
intErr = 0.0
lastErr = 0.0
lastT = ts[0]

lastG = 0.0

i = 0
d = 0
exp = -np.exp(-1/tau)
mp = 0

# Motor equations
#
# Ts = kt * (V/R)
#    Ts is stall torque
#    V is applied voltage (e.g., 0 to 12 Volts)
#    R is coil resistance (e.g. 9.16E-2 Ohm for CIM)
#
# wf = (kt/ke)*(V/R)
#    wf is final angular rate at zero torque
#    kt is defined by stall torque at applied voltage
#    ke is ideally kt, but in reality it is usually slightly different
#
# T = Ts(1 - (w/wf))
#    T is the torque at a specific angular rate
#
# w_dot = T/J
#    w_dot is angular acceleration
#    J is moment of inertial

for t in ts:
    if (t > 0):
        sps[i] = math.sin(sp_period*t)
        sps[i] = sps[i] / abs(sps[i])   # Square wave
    else:
        sps[i] = 0
        
    derr = err - lastErr
    intErr = intErr + err
    mv = kf*sps[i] + (kp * err) + (ki * intErr) + (kd * (derr/dt))
    mvs[i] = mv
    mp = mp + (mv * dt)
    mps[i] = mp
    G = 0.0
    if (t >= delay):
        G = mp * Gp * (1.0 + exp) - (lastG * exp)
    else:
        d += 1
    
    pvs[i] = G
    lastG = G

    i += 1
    
    lastErr = err
    err = 0.0
    if (t >= delay):
        err = sps[i-d] - pvs[i-d]
        
    #err += np.random.randn(1)*0.04
    
    
plot.figure(1)
plot.cla()
plot.grid()
plot.plot(ts,sps,ts,pvs)
    
    
    
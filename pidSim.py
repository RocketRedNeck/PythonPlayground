# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 21:57:29 2016

@author: mtkes
"""

import matplotlib.pyplot as plot
import numpy as np

tmax_sec = 5.0
dt_sec = 0.001
ts_sec = np.arange(0.0, tmax_sec, 0.001)
nmax = round(tmax_sec/dt_sec)
ns = range(0, nmax)

pvFinal = np.zeros(nmax+1)


kp = 0.1    # Proportional gain
ki = 0.2    # Integral gain
kd = 0.0    # Derivative gain
kg = 1.0    # Plant (Process) gain

delay_sec = 1 * dt_sec
tau_sec   = 1 * dt_sec
 

sp  = 1.0
err = 0.0
intErr = 0.0
lastErr = 0.0


G = 0.0     # Process output to be measured

i = 0
d = 0
exp = np.exp(-1/tau_sec)

pidPeriod_sec    = 0.02;
pidPeriod_index  = round(pidPeriod_sec / dt_sec)
pidStart_index   = 0        # "time" that PID computation started
pidDuration_sec  = 0.001    # Time to complete PID calculation (models software latency)
pidDuration_index = round(pidDuration_sec / dt_sec)
pidEnd_index      = pidDuration_index    # "time" that PID computation ended
pidJitter_sec    = 0.0  # Later we will add a "random" jitter that delays the PID task
pidJitter_index  = round(pidJitter_sec / dt_sec)

cvPid   = np.zeros(nmax+1)  # Initial value of cv coming from PID calculation

comm0Start_index = 0         # "time" that first communication bus starts
comm0Delay_sec   = 0.001     # Time to complete communication (MUST BE LESS THAN PID PERIOD)
comm0Delay_index = round(comm0Delay_sec / dt_sec)
comm0End_index   = comm0Delay_index
comm0Jitter_sec  = 0.0  # Later we will add a "random" jitter that delays communication
comm0Jitter_index = round(comm0Jitter_sec / dt_sec)

cvComm0 = np.zeros(nmax+1)  # cv value delayed for first communication bus

camOffset_sec  = 0.0        # Offset to represent asynchronous camera start
camOffset_index = round(camOffset_sec / dt_sec)
camStart_index = camOffset_index          # "time" that camera runs
camRate_Hz     = 24         # Camera frame rate
camPeriod_sec  = 1.0/camRate_Hz
camPeriod_index = round(camPeriod_sec / dt_sec)
camEnd_index   = camPeriod_index
camImage_index = (camStart_index + camEnd_index) / 2    # Time associated with center of image

pvCam = np.zeros(nmax+1)    # process variable delayed for camera framing

for n in ns:
    
    # Only run the PID calculation on a period boundary
    # i.e., this branch represents the task scheduled on a boundary
    # When jitter is enabled we will occasionally add a delay
    # representing a late task start (independent of measurement jitter)
    # We assume here that the task is delayed and not immediately preempted
    # and thus able to make full use of its time slice
    if ((n % (pidPeriod_index + pidJitter_index)) == 0):
        pidStart_index = n
        pidEnd_index = pidStart_index + pidDuration_index
        
        # Once we get going, we can compute the error as the
        # difference of the setpoint and the latest output
        # of the process variable (delivered after all sensor and
        # communication delays)
        if (n > 0):
            err = sp - pvFinal[n-1]
        
        # Assume we currently have no way of directly measuring derr
        # so we use the err measurement to estimate the error rate
        # In this sense, the error rate is an average over the
        # previous interval of time since we last looked, thus the
        # error rate is in the past
        derr = err - lastErr
        lastErr = err
        
        # Integrate the error (i.e., add it up)
        intErr = intErr + err
        
        # Compute the control variable by summing the PID parts
        # When the pidEnd_index is reached, the output will be
        # forwarded to the communication sequence
        cvPid[n] = (kp * err) + (ki * intErr) + (kd * (derr/pidPeriod_sec))
        
    elif (n > 0):   # Previous output is held until the next task wakeup time
        cvPid[n] = cvPid[n-1] 
    
    # Initiate communication delay
    if (n == pidEnd_index):
        comm0Start_index = n
        comm0End_index = comm0Start_index + comm0Delay_index + comm0Jitter_index
        
    # When communication delay has been met, move the information along
    if (n == comm0End_index):
        cvComm0[n] = cvPid[comm0Start_index]
    elif (n > 0):   # Otherwise, just hold the previous command
        cvComm0[n] = cvComm0[n-1]
        
    # Currently just model the motor, gears, and kinematics as a simple
    # time constant without limits
    # We will likely improve this fidelity later by adding limiting
    # The kinematics (physics) runs "continuously" so we update it
    # every time step
    G = (kg * cvComm0[n] * (1.0 - exp)) + (G * exp)
    
    # Next is the sensor delay, communication, processing, and communication
    # on the return path
    
    # The process output will be sensed by a camera and delivered at the
    # camera frame rate; the frame interval is asynchronous to all other
    # processing periods.
    # We currently assume insignificant jitter in the camera rate
    # We also are neglecting any blur occuring due to motion
    #
    # However, we will pick a point midway in the frame to represent
    # the time of the relevant image data; depending on the simulation
    # time step and modeled frame rate for the camera can cause a jitter
    # of up to a time step 
    if ((n % camPeriod_index) == camOffset_index):
        camStart_index = n
        camEnd_index = camStart_index + camPeriod_index
        camImage_index = (camStart_index + camEnd_index)/2  # Midpoint in time
    
    # Capture the process variable at the image center time
    # This is a point in time associated with the center pixel of
    # the image. or now we will just assume that the item we will measure in the
    # image is at the same point in time as the image center.
    # Reality is that the difference is small and only important for
    # very rapid target motion
    if (n == camImage_index):
        pvCam[n] = G
    elif (n > 0):
        pvCam[n] = pvCam[n-1]   # Hold previous camera values until next update
    
    # Image processing is assumed to operate as fast as it can
    # but will have asynchronous start and duration will vary based on
    # image content with a well defined lower and upper limit.    
    
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
    
    
    
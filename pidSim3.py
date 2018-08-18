# -*- coding: utf-8 -*-
"""
pidSim3.py

A simulation of a vision control to steering PID loop accounting for communication and
processing latency and variation; demonstrates the impact of variation
to successful control.

THIS VERSION models the control as a second order input (torque to acceleration)
and then integrates twice to get position. The result is that derivative control
will be required account for the integration lag. In other words, the control
variable (CV) has indirect control over the process variable (PV) and motor speed
control is handled by this loop. If the motor speed is controlled via a separate
motor controller then the implicit cascaded PID of that controller is demonstrated
by pidSim2.

This allows students to experiment with how different elements in the scaling
of a control loop affect performance, this focusing efforts on successful
design.

The model consists of a PID processing software with an asynchronous alignment
with a camera frame which is also asynchronous to image processing software.
Communication latency and jitter are planned as well as image processing impacts.

A plot at the end shows a sample over some specified duration.

The initial conditions of the file represents a case that won't work well until
it is correct by improvements in the constants and image processing rates

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
**************************************************************************************************** 
"""

import matplotlib.pyplot as plot
import numpy as np

tmax_sec = 5.0
dt_sec = 0.001
ts_sec = np.arange(0.0, tmax_sec, 0.001)
nmax = ts_sec.__len__() # round(tmax_sec/dt_sec)
ns = range(0, nmax)


kp = 0.0    # Proportional gain
ki = 0.0    # Integral gain
kd = 0.8   # Derivative gain
kg = 1.0    # Plant (Process) gain

tau_sec   = 0.3  # Assume motor torque response is nearly instantaneous
 

sp  = np.zeros(nmax)        # Will initialize after first image processed
err = np.zeros(nmax)
intErr = np.zeros(nmax)
derrdt = np.zeros(nmax)

lastErr = 0.0


G = np.zeros(nmax)     # Process output to be measured

exp = np.exp(-dt_sec/tau_sec)

# Define a mass property for scaling later
# in this case we just use a scalar to represent either linear or rotation
m = 1

# Define arrays to hold the kinematic values
# In this case we will use simple names to represent either linear or rotation
a = np.zeros(nmax)     # linear or angular acceleration
v = np.zeros(nmax)     # linear or angular velocity
p = np.zeros(nmax)     # linear or angular position




# Model of the pid task via a java util.timer
# We add a random normal variation for task wakeup since the util.timer
# can only assure that the task wakes up no earlier than scheduled.
# Empirical measurement of the task latency is required for accurate
# modeling, but for now we can just assume about a 10% average
pidPeriod_sec    = 0.01;
pidPeriod_index  = round(pidPeriod_sec / dt_sec)
pidStart_index   = 0        # "time" that PID computation started
pidDuration_sec  = 0.0001    # Time to complete PID calculation (models software latency)
pidDuration_index = round(pidDuration_sec / dt_sec)
pidEnd_index      = pidStart_index + pidDuration_index    # "time" that PID computation ended
pidMinJitter_sec    = 0.000   # Minimum Random task jitter
pidMinJitter_index  = round(pidMinJitter_sec / dt_sec)
pidMaxJitter_sec    = 0.000   # Maximum Random task jitter
pidMaxJitter_index  = round(pidMaxJitter_sec / dt_sec)
pidMeanJitter_index = round((pidMaxJitter_index + pidMinJitter_index)/2)
pidStdDevJitter_index = round((pidMaxJitter_index - pidMinJitter_index) / 3)


cvPid   = np.zeros(nmax)  # Initial value of cv coming from PID calculation

# The first communication link is assumed to be a CAN bus
# The bus overhead is assumed to be a total fixed time
# not exceeding about 1 ms for up to four (4) messages going to four (4)
# separate motors (including any increases for bit stuffing); in other words
# we assume something like 100 bits per message all mastered from the same
# location on a 1 Mbps bus.
# The underlying software is assumed to be some queue processing task that
# wakes upon a posted message. A complete review of the path is needed to
# assess whether to task that actually receives the posted message awakens
# immediately (higher priority) or must time slice with all other concurrent
# tasks. If communication tasking is forced to wait for an available cycle
# it is possible that an indeterminate delay may occur at the post-to-wire
# boundary; also, the communication tasking must post all messages queued
# to the wire in close sequence otherwise the motors will be out of phase
# We can inject an estimate of communication jitter as a whole using a
# simple normal distribution
comm0Start_index = 0         # "time" that first communication bus starts
comm0Delay_sec   = 0.001     # Time to complete communication (MUST BE LESS THAN PID PERIOD)
comm0Delay_index = round(comm0Delay_sec / dt_sec)
comm0End_index   = comm0Start_index + comm0Delay_index
comm0MinJitter_sec  = 0.000 
comm0MinJitter_index = round(comm0MinJitter_sec / dt_sec)
comm0MaxJitter_sec  = 0.000
comm0MaxJitter_index = round(comm0MaxJitter_sec / dt_sec)
comm0MeanJitter_index = round((comm0MaxJitter_index + comm0MinJitter_index)/2)
comm0StdDevJitter_index = round((comm0MaxJitter_index - comm0MinJitter_index) / 3)

cvComm0 = np.zeros(nmax)  # cv value delayed for first communication bus

camOffset_sec  = 0.0        # Offset to represent asynchronous camera start
camOffset_index = round(camOffset_sec / dt_sec)
camStart_index = camOffset_index          # "time" that camera runs
camRate_Hz     = 12         # Camera frame rate
camPeriod_sec  = 1.0/camRate_Hz
camPeriod_index = round(camPeriod_sec / dt_sec)
camEnd_index   = camStart_index + camPeriod_index
camImage_index = round((camStart_index + camEnd_index) / 2)    # Time associated with center of image

pvCam = np.zeros(nmax)    # process variable delayed for camera framing

# The second communication bus is polled by the imaging software
# The time that the imaging software starts is asynchronous to the
# other system components, and it will not execute again until the
# image processing completes (which itself has some variation)
comm1Start_index = 0         # "time" that second communication bus starts
comm1Delay_sec   = 0.020     # Time to complete communication
comm1Delay_index = round(comm1Delay_sec / dt_sec)
comm1End_index   = comm1Start_index + comm1Delay_index
comm1MinJitter_sec  = 0.000 
comm1MinJitter_index = round(comm1MinJitter_sec / dt_sec)
comm1MaxJitter_sec  = 0.000 
comm1MaxJitter_index = round(comm1MaxJitter_sec / dt_sec)
comm1MeanJitter_index = round((comm1MaxJitter_index + comm1MinJitter_index)/2)
comm1StdDevJitter_index = round((comm1MaxJitter_index - comm1MinJitter_index) / 3)
    
pvComm1 = np.zeros(nmax)  # pv value delayed for second communication bus

# Image processing consists of a bounded, but variable process
# The content of the image and the operating environment will cause the 
# associated software to vary; we will use emprical estimates for a current
# approach and will assume the variation has a normal distribution with a
# 3-sigma distribution between the upper and lower limits
pvImageStart_index = 0
pvImageMaxRate_Hz = 30.0
pvImageMinRate_Hz = 10.0
pvImageRateSigma = 3
pvImageMaxDuration_sec = 1.0 / pvImageMinRate_Hz
pvImageMinDuration_sec = 1.0 / pvImageMaxRate_Hz
pvImageMaxDuration_index = round(pvImageMaxDuration_sec / dt_sec)
pvImageMinDuration_index = round(pvImageMinDuration_sec / dt_sec)
pvImageMeanDuration_index = round((pvImageMinDuration_index + pvImageMaxDuration_index)/2)
pvImageStdDevDuration_index = round((pvImageMaxDuration_index - pvImageMinDuration_index) / pvImageRateSigma)
    
pvImageEnd_index = pvImageStart_index + 2*pvImageMaxDuration_index

pvImage = np.zeros(nmax)

# Final communication link between image processing and the PID
comm2Start_index = 2*pvImageMaxDuration_index # "time" that third communication bus starts (always after image processing)
comm2Delay_sec   = 0.020     # Time to complete communication
comm2Delay_index = round(comm2Delay_sec / dt_sec)
comm2End_index   = comm2Start_index + comm1Delay_index
comm2Jitter_sec  = 0.0  # Later we will add a "random" jitter that delays communication
comm2Jitter_index = round(comm2Jitter_sec / dt_sec)

pvComm2 = np.zeros(nmax)  # pv value delayed for third communication bus


pvFinal = np.zeros(nmax)

for n in ns:
    
    # Only run the PID calculation on a period boundary
    # i.e., this branch represents the task scheduled on a boundary
    # When jitter is enabled we will occasionally add a delay
    # representing a late task start (independent of measurement jitter)
    # We assume here that the task is delayed and not immediately preempted
    # and thus able to make full use of its time slice
    if (pidStdDevJitter_index == 0):
        pidJitter_index = 0
    else:
        pidJitter_index = round(np.random.normal(pidMeanJitter_index, pidStdDevJitter_index))
        
    if ((n % (pidPeriod_index + pidJitter_index)) == 0):
        #print("@ " + str(n) + " pid start")
        pidStart_index = n
        pidEnd_index = pidStart_index + pidDuration_index
        
        # Once we get going, we can compute the error as the
        # difference of the setpoint and the latest output
        # of the process variable (delivered after all sensor and
        # communication delays)
        if (n > 0):
            err[n] = sp[n] - pvFinal[n-1]
        
        # Assume we currently have no way of directly measuring derr
        # so we use the err measurement to estimate the error rate
        # In this sense, the error rate is an average over the
        # previous interval of time since we last looked, thus the
        # error rate is in the past
        derrdt[n] = (err[n] - err[n-1]) / pidPeriod_sec
        
        # Integrate the error (i.e., add it up)
        intErr[n] = intErr[n-1] + err[n]
        
        # Compute the control variable by summing the PID parts
        # When the pidEnd_index is reached, the output will be
        # forwarded to the communication sequence
        cvPid[n] = (kp * err[n]) + (ki * intErr[n]) + (kd * derrdt[n])
        
    elif (n > 0):   # Previous output is held until the next task wakeup time
        err[n] = err[n-1]
        derrdt[n] = derrdt[n-1]
        intErr[n] = intErr[n-1]
        cvPid[n] = cvPid[n-1] 
    
    # Initiate communication delay
    if (n == pidEnd_index):
        #print("@ " + str(n) + " pid end = " + str(cvPid[n]))
        comm0Start_index = n
        if (comm0StdDevJitter_index == 0):
            comm0Jitter_index = 0
        else:
            comm0Jitter_index = round(np.random.normal(comm0MeanJitter_index, comm0StdDevJitter_index))
        
        comm0End_index = comm0Start_index + comm0Delay_index + comm0Jitter_index
        
    # When communication delay has been met, move the information along
    if (n == comm0End_index):
        cvComm0[comm0End_index] = cvPid[comm0Start_index]
        #print("@ " + str(n) + " comm0 end = " + str(cvComm0[comm0End_index]))
    elif (n > 0):   # Otherwise, just hold the previous command
        cvComm0[n] = cvComm0[n-1]
        
    # Currently just model the motor, gears, and kinematics as a simple
    # time constant without limits
    # The kinematics (physics) runs "continuously" so we update it
    # every time step
    
    # First, model a simple time constant representing motor torque (moment, M)
    G[n] = (kg * cvComm0[n] * (1.0 - exp)) + (G[n-1] * exp)
    
    # Torque applied to the robot mass induced motion
    # We don't yet care about the specific (how much mass nor whether the
    # motion is linear or rotational); in this case all we want to demonstrate
    # is the process effects of integrating from force to a position representing
    # the process variable being compared to the set point
    #
    # The form is F = m a or M = I alpha, but we will just use simple names
    # here
    a[n] = G[n] / m
    
    # Integrate to a velocity
    # Here will use a simple trapezoidal rule; we can upgrade this to Runge-Kutta
    # or other methods later but if our time step is small enough compared to
    # the rate of change, then trapezoidal is fine
    if (n > 0):
        v[n] = v[n-1] + a[n-1]*dt_sec + (a[n] - a[n-1])*dt_sec/2

    # Integrate to a position
    if (n > 0):
        p[n] = p[n-1] + v[n-1]*dt_sec + (v[n] + v[n-1])*dt_sec/2
    
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
        #print("@ " + str(n) + " camera start")
        camStart_index = n
        camEnd_index = camStart_index + camPeriod_index
        camImage_index = round((camStart_index + camEnd_index)/2)  # Midpoint in time

    # This is a point in time associated with the center pixel of
    # the image. For now we will just assume that the item we will measure in the
    # image is at the same point in time as the image center.
    # Reality is that the difference is small and only important for
    # very rapid target motion
    
    # While the center point of the image time is important for averaging
    # state on the image data, the frame will not be deliverable until the
    # entire frame is ready for the next communication boundary (when the frame
    # can be fetched)
    if (n == (camEnd_index-1)):
        pvCam[camStart_index:camEnd_index] = p[camImage_index]
        #print("@ " + str(n) + " camera = " + str(G[camImage_index]))
    
    # Image processing is assumed to operate as fast as it can
    # but will have asynchronous start and duration will vary based on
    # image content with a well defined lower and upper limit.
    #
    # The modeling is a small communication delay followed by a variable
    # image processing delay; we will model a small normal distribution in
    # time but will not model imaging errors
    
    if (n == comm1Start_index):
        #print("@ " + str(n) + " COMM1 start")
        if (comm1StdDevJitter_index == 0):
            comm1Jitter_index = 0
        else:
            comm1Jitter_index = round(np.random.normal(comm1MeanJitter_index, comm1StdDevJitter_index))
            
        comm1End_index = comm1Start_index + comm1Delay_index + comm1Jitter_index
    
    # Whichever image frame is available will now be forwarded
    # We back up one camera period from when communication startsbecause the
    # image information won't be available while a frame is being sampled
    # The information is placed in the outgoing comm1 buffer at the end of 
    # communication, effectively delaying the image information and keeping
    # the boundaries aynchronous to the resolution of the time step.    
    if (n == comm1End_index):
        if (comm1Start_index >= camPeriod_index):
            pvComm1[comm1End_index] = pvCam[comm1Start_index - camPeriod_index]
        else:
            pvComm1[comm1End_index] = pvCam[comm1Start_index]
        
        #print("@ " + str(n) + " COMM1 end = " + str(pvComm1[comm1End_index]))
        # Now that communication has completed, the image processing
        # can start; here we represent a variable processing latency
        # as a normal distribution between a min and max time assumed
        # to be 3-sigma limit
        # This is not a precise model of the statistical variation
        # of actual image processing, but rather just enough variation
        # to observe the impact to a control loop (if any)
        pvImageStart_index = comm1End_index

        if (pvImageStdDevDuration_index == 0):
            pvImageJitter_index = pvImageMeanDuration_index
        else:
            pvImageJitter_index = round(np.random.normal(pvImageMeanDuration_index, pvImageStdDevDuration_index))
        
        
        pvImageEnd_index = pvImageStart_index + pvImageJitter_index
        
    elif (n > 0):
        pvComm1[n] = pvComm1[n-1]

    # When image processing is complete, we can begin to send the result
    # to the final communication link and then restart the second comm link
    # to read the camera again
    if (n == pvImageEnd_index):
        pvImage[pvImageEnd_index] = pvComm1[comm1End_index]
        #print("@ " + str(n) + " IMAGE PROCESSING end = " + str(pvImage[pvImageEnd_index]))
        comm2Start_index = pvImageEnd_index
    elif (n > 0):
        pvImage[n] = pvImage[n-1]
        
    if (n == comm2Start_index):
        comm2End_index = comm2Start_index + comm2Delay_index
        #print("@ " + str(n) + " COMM2 start --> end = " + str(comm2End_index))
        
    if (n == comm2End_index):
        pvComm2[comm2End_index] = pvImage[comm2Start_index]
        #print("@ " + str(n) + " COMM2 end = " + str(pvComm2[comm2End_index]))
        comm1Start_index = comm2End_index + 1    # Restart image processing immediately

        # Enforce causality
        # We delay the awareness of the set point until after the first
        # image is processed and communicated; it is only at that moment
        # the system becomes aware of the error
        if (n < nmax-1):
            sp[n+1] = 1.0       
        
    elif (n > 0):
        pvComm2[n] = pvComm2[n-1]
        if (n < nmax-1):
            sp[n+1] = sp[n]
        
    pvFinal[n] = pvComm2[n]
    
    
plot.figure(1)
plot.cla()
plot.grid()
plot.plot(ts_sec,sp,label='sp')
plot.plot(ts_sec,err,label='err')
#plot.plot(ts_sec,cvPid,label='cvPid')
#plot.plot(ts_sec,cvComm0,'o',label='cvComm0')
#plot.plot(ts_sec,G,label='G')
plot.plot(ts_sec,p,label='p')
plot.plot(ts_sec,pvCam,label='CameraFrame'),
plot.plot(ts_sec,pvComm1,label='CamComm+ImageProcessing')
plot.plot(ts_sec,pvImage,label='NetworkTableStart')
plot.plot(ts_sec,pvComm2,label='NetworkTableEnd')
#plot.plot(ts_sec,pvFinal,label='pvFinal')
#plot.legend()
plot.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

    
    
    
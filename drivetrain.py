# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 23:19:35 2018

@author: RocketRedNeck
"""

#define build "20130924_2231"

# https:#www.chiefdelphi.com/media/papers/2868
# https:#www.chiefdelphi.com/media/papers/3022
# https:#www.chiefdelphi.com/forums/showthread.php?p=1295286#post1295286
# Java variant: https:#github.com/brennonbrimhall/DrivetrainCalculator

#include <math.h>
#include <stdio.h>
import matplotlib.pyplot as plot
import numpy as np
import math


# The following constants define the drivetrain being modeled:

#set xstop=15


# note: k1, k2, & k3 have been renamed Kro, Krv, & Kf
Kro = 10;  # rolling resistance tuning parameter, lbf (non-speed-dependent non-torque-dependent constant friction force in pounds)
Krv = 0;   # rolling resistance tuning parameter, lbf/(ft/sec) (speed-dependent losses, pounds per ft/sec)
Kf = 0.7;  # drivetrain efficiency fraction (drivetrain torque efficiency fraction, unitless, range 0 to 1)

Vspec = 12;   # motor spec volts
Tspec = 343.4;   # motor stall torque, in_oz
Wspec = 5310; # motor free speed, RPM
Ispec = 133;  # motor stall amps
n=4;             # number of motors

G = 12.75;  # gear ratio
r = 3;  # wheel radius, inches

M  = 150;  # vehicle mass, lbm
uk = 0.8;  # coefficient of kinetic friction
us = 1.0;  # coefficient of static friction

Rcom = 0.013; # ohms, battery internal resistance plus
                     # wire and connection resistance
					 # from battery to PDB (including main breaker)
					 
Vbat = 12.7;  # fully-charged open-circuit battery volts

Rone = 0.002;  # ohms, circuit wiring and connector resistance
                      # from PDB to motor (including 40A breaker)
				  
dt = 0.001  # integration step size, seconds
tstop = 3.0 # integration duration, seconds

ts = np.arange(0.0, tstop, dt)



# -------------- end of user-defined constants -----------------

 # derived constants:
#Toffset, Tslope,  # offset and slope of adjusted Torque vs Speed motor curve
#Kt,  # motor torque constant, Nm/amp
#Vfree,  # vehicle speed at motor free speed, meters/sec
#W,  # vehicle weight, Newtons
#F2A; # force to amps

# working variables:

slipping = np.zeros(len(ts));  # state variable, init to zero
A = np.zeros(len(ts));     # Current at the motor
Vm = np.zeros(len(ts));     # Voltage at the motor
a = np.zeros(len(ts))  # acceleration, m/s^2
V = np.zeros(len(ts))  # vehicle speed, meters/sec
x = np.zeros(len(ts))  # vehicle distance traveled, meters
#t,  # elapsed time, seconds
#       a,  # vehicle acceleration, meters/sec/sec
#	   A;  # current per motor, amps

Kro *= 4.448222;  # convert lbf to Newtons
Krv *= 4.448222*3.28083; # convert lbf/(ft/s) to Newtons/(meter/sec)
Tspec *= 0.00706155;  # convert oz_in to Newton_meters
Wspec = Wspec/60*2*3.1415926536; # convert RPM to rad/sec
r = r*2.54/100;  # convert inches to meters
M *= 0.4535924;  # convert lbm to kg

# calculate Derived Constants once:
#Toffset = (Tspec*Vbat*Wspec)/(Vspec*Wspec+Ispec*Rone*Wspec+Ispec*n*Rcom*Wspec);
Tslope = (Tspec*Vspec)/(Vspec*Wspec+Ispec*Rone*Wspec+Ispec*n*Rcom*Wspec);
Kt = Tspec/Ispec;
W = M*9.80665;
F2A = r/(n*Kf*G*Kt); # vehicle total force to per-motor amps conversion

def Toffset(volts):
    return (Tspec*volts*Wspec)/(Vspec*Wspec+Ispec*Rone*Wspec+Ispec*n*Rcom*Wspec)

def accel(Vi,i):  # compute acceleration w/ slip

#Wm, # motor speed associated with vehicle speed
#L,  # rolling resistance losses, Newtons
#Tm, # motor torque, Newtons
#Tw, # wheel torque, Newtons
#Ft, # available vehicle force due to wheel torque, Newtons
#F,  # slip-adjusted vehicle force due to wheel torque, Newtons
#Fa; # vehicle accel force, Newtons
    global slipping
    Wm = Vi/r*G;
    Tm = Toffset(Vbat)-Tslope*Wm; # available torque at motor @ V
    Tw = Kf*Tm*G; # available torque at one wheel @ V
    Ft = Tw/r*n;  # available force at wheels @ V
    if (Ft>W*us):
        slipping[i]=1;
    else:
        if (Ft<W*uk):
            slipping[i]=0;
    if (slipping[i] != 0):
        F = W*uk
    else:
        F = Ft
    global A
    A[i] = F*F2A;    # computed here for output
    global Vm
    Vm[i] = Vbat-n*A[i]*Rcom-A[i]*Rone;  # computed here for output
    L = Kro+Krv*Vi; # rolling resistance force (add a *V*V term for air resistance if you really, really think it is necessary)
    Fa = F-L; # net force available for acceleration
    if (Fa<0):
        Fa=0;
    return Fa/M;

#def print:
#    printf("%f,%f,%f,%d,%f,%f,%f\n",t,x*3.28083,V*3.28083,slipping,a*3.28083,n*A/10,Vm);

def Heun(): # numerical integration using Heun's Method
    #Vtmp, atmp; # local scratch variables
    i = 1
    global a
    global x
    global V
    for t in ts[1:]:
        Vtmp = V[i-1]+a[i-1]*dt;  # kickstart with Euler step
        atmp = accel(Vtmp,i);
        Vtmp = V[i-1]+(a[i-1]+atmp)/2*dt; # recalc Vtmp trapezoidally
        a[i] = accel(Vtmp,i);  # update a
        x[i] = x[i-1] + (V[i-1]+Vtmp)/2*dt;  # update x trapezoidally
        V[i] = Vtmp;            # update V
        if (a[i] < 0.05): # Not really getting much faster. Stop the sim when acceleration is under 5 cm/s^2
            break
        i = i + 1
        #print();

# for reference only; not used:
#def Euler: # numerical integration using Euler's Method
#    for (t=dt; t<=tstop; t+=dt) 
#    {
#        V+=a*dt;
#        x+=V*dt;
#        a = accel(V); 
#        #print();
#    }



if __name__ == '__main__':

    #printf("t,feet,ft/s,slip,ft/s/s,amps/10,Vm,%s Kro=%4.1f Krv=%4.1f Kf=%3.1f Vspec=%3.1f Tspec=%4.1f Wspec=%5.0f Ispec=%4.1f Rcom=%4.3f Vbat=%4.2f Rone=%4.3f n=%d G=%5.2f r=%3.1f M=%3.0f uk=%3.2f us=%3.2f\n",
    #build,Kro,Krv,Kf,Vspec,Tspec,Wspec,Ispec,Rcom,Vbat,Rone,n,G,r,M,uk,us); # prCSV header
    
    #English2SI();
    

    
    a[0]=accel(V[0],0); # compute accel at t=0
    ##print();    # output values at t=0
    
    Heun();  # numerically integrate and output using Heun's method
    
    plot.figure(1)
    plot.cla()
    plot.grid()
    plot.plot(ts,x,ts,V,ts,a,ts,slipping,ts,Vm,ts,A/10)
    plot.legend(['x','V','a','slipping','Volts','Amps/10'])


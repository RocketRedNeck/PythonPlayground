# -*- coding: utf-8 -*-
"""
odeExample - example of integration of ordinary differential equations in the
             form of an understandable physical system that can be visualized
             by middle and high school students

    Equations of motion of a shot put and plastic-like ball with drag in 
    2-dimensions
    
    NOTE: We won't be modeling the actual plastic ball aerodynamics, just the
    mass and diameter as it is effected by simple drag on a sphere.
 
    Definitions
    -----------
        px = x-component of position
        py = y-component of position
        vx = x-component of velocity --> dpx/dt
        vy = y-component of velocity --> dpy/dt
        ax = x-component of acceleration --> dvx/dt
        ay = y-component of acceleration --> dvy/dt
    
        Fx = x-component of drag force
        Fy = y-component of drag force
    
        Cd = drag coefficient
        rho = air density
        A = cross section area
    
        m = mass
    
        g = acceleration due to gravity
    
        SIMPLIFY: Cd, rho, A and g are constant                    
        SIMPLIFY: Cd and A are directionally invariant (i.e., a sphere)

        REALITY: g(p) is gravity as a function of position
                 rho(p) is density as a function of position
                 A depends on the direction of flow across the body being 
                 considered
                 Cd depends on the speed and direction of flow across the body 
                 being considered
                 i.e., Cd depends on a value known as the Reynolds number (Re), 
                 which is a ratio of inertia forces and visous forces
                     Re = v*rho*l/mu
                     l is a reference distance
                     mu is a viscosity coefficient
                     
                FORTUNATELY, the Cd is constant over a wide range of Re for
                a sphere (i.e., ~0.5 from Re about 10^3 to 10^5)
                
                See: https://www.grc.nasa.gov/WWW/K-12/airplane/dragsphere.html
                
                Interestingly: http://www.rpi.edu/dept/chem-eng/WWW/faculty/plawsky/Comsol%20Modules/plastic/WiffleBallAerodynamics.pdf
                
                Without the assumptions we would have to model Cd(Re(v)), which
                we may do in a second version of this example.
    
        q(v) = Dynamic pressure as function of velocity = 0.5*rho*v^2
        F(v) = Drag force as function of velocity = -(|v|/v)*Cd*A*q(v)
              i.e., Drag is in the opposite direction of velocity

    Equations
    ---------
        dpx_dt = vx
        dpy_dt = vy
        dvx_dt = F(vx)/m        Remember F= m*a --> a = F/m
        dvy_dt = F(vy)/m - g
       
        Make it pythonic by assigning 
            
            p[0] is px
            p[1] is py
            v[0] is vx
            v[1] is vy
        
        Represent as a single state vector:
            
            s[0] is px
            s[1] is py
            s[2] is vx
            s[3] is vy
            
        Create a function of the following form:
            
            ds = f(t,s)
            
            where
            
            ds[0] = s[2]            | These are the equations
            ds[1] = s[3]            |
            ds[2] = F(s[2])/m       |
            ds[3] = F(s[3])/m - g   |
                        
        Continue on to the code below to see how to run a simulation of this
        system of equations
                     
Copyright (c) 2018 - RocketRedNeck / Michael Kessel

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

from scipy.integrate import ode
import scipy.constants as const
import math
import numpy as np
import matplotlib.pyplot as pl

"""
q is the dynamic pressure - the presure cause by the motion through the fluid
"""
def q(v,rho):
    return 0.5*rho*v**2

"""
Fdrag is the drag on an object with the specified coefficient, cross sectional
area, local air density and current speed, v
"""
def Fdrag(v,Cd,A,rho):
    return -(abs(v)/v)*Cd*A*q(v,rho)

"""
Fbouyancy is the bouyant force of an object in the fluid
"""
def Fbouyancy(V,rho):
    return rho*V*const.g

"""
Fmagnus is the magnus force on the spinning ball

  Fundamentally to get the Magnus effect we can approximate the
  lift as described here: https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/beach.html
  This derived from the description of Kutta-Joukowski lift on a rotating
  cylinder
  
  F/L = r * v * G
  
  where G is vortex strength (basically the rotation creating a radial pressure gradient
  that induced the pressure drop that causes the force on the object)
  
  G = 2*rho*r^2 * w
  w = rotation rate
  
  The force produced by the rotation in a flow is then:
      
  F = (r * G * v) * (2 * b) * (pi / 4)
  
  b = ball radius = r, the cylinder radius
"""
def Fmagnus(v,r,w,rho):
    G = 2.0 * rho * (r**2) * w
    return (r * G * v) * 2.0 * r * const.pi / 4.0

"""
F is the total force due to drag and buoyancy, a convenience function
for initialization

NOTE: We have not included the Magnus effect for a rotating ball because
it needs to be incorporated perpendicular to the velocity     
"""
def F(v,Cd,A,V,rho):
    return Fdrag(v, Cd, A, rho) + Fbouyancy(V, rho)

"""
f is the system of equations we want to model with arguments for parameterizing
the system
"""
def f(t, s, Cd, A, V, m, rho_fluid, rho_object, r, w):
    # Prevent downward velocity from exceeding terminal velocity
    # This prevent the integrator from exceeding physics before
    # it is incorporated into the next step
    #
    # From Fdrag + Fbuoyancy = mg (i.e., weight, mg = V*rho_object*g)
    vterminal= math.sqrt((2*const.g/(Cd*A/V)*(rho_object/rho_fluid - 1)))
    vx = s[2]
    vy = s[3]
    if (vy < -vterminal):
        vy = -vterminal
        
    ax = (Fdrag(vx, Cd, A, rho_fluid) - Fmagnus(vy,r,w,rho_fluid))/m
    ay = (Fdrag(vy, Cd, A, rho_fluid) + Fbouyancy(V, rho_fluid) + Fmagnus(vx,r,w,rho_fluid))/m
    
    return [vx, 
            vy, 
            ax, 
            ay - const.g]
    
# Define some constants for each case
    
rho_kgpm3 = 1.225   # Air density standard sea level Kg/m^3
Cd = 0.5            # Smooth sphere drag coefficient at Re between approximately 10^3 and 10^5

# Ball information
# https://www.topendsports.com/resources/equipment-ball-size.htm
m_shotput_kg = 7.26         # Men's shot put mass in Kg
d_shotput_m = 0.120         # Average diameter of shot put in meters (m)
r_shotput_m = d_shotput_m / 2.0
A_shotput_m2 = const.pi * r_shotput_m**2   # Cross section area of shot put m^2
V_shotput_m3 = (4.0/3.0) * const.pi * r_shotput_m**3
rho_shotput_kgpm3 = m_shotput_kg/V_shotput_m3


# plastic ball mass and diameter but NOT the aerodynamic characterstics
m_plastic_kg = 0.045        # Average plastic ball mass in Kg
d_plastic_m = 0.0765        # Average diameter of plastic ball in meters (m)
r_plastic_m = d_plastic_m/ 2.0
A_plastic_m2 = const.pi * r_plastic_m**2   # Cross section area of plastic m^2
V_plastic_m3 = (4.0/3.0) * const.pi * r_plastic_m**3
m_plastic_kg += V_plastic_m3 * rho_kgpm3    # Air inside sealed ball
rho_plastic_kgpm3 = m_plastic_kg/V_plastic_m3

# WBeach ball mass and diameter
m_beach_kg = 0.022         # Average 12" Beach ball mass in Kg
d_beach_m = 0.3048         # Average diameter of beach ball in meters (m)
r_beach_m = d_beach_m / 2.0
A_beach_m2 = const.pi * r_beach_m**2   # Cross section area of beach ball m^2
V_beach_m3 = (4.0/3.0) * const.pi * r_beach_m**3
m_beach_kg += V_beach_m3 * rho_kgpm3        # Air inside sealed ball
rho_beach_kgpm3 = m_beach_kg/V_beach_m3

# Define an Olympian for the initial state
# https://www.brunel.ac.uk/~spstnpl/BiomechanicsAthletics/ShotPut.htm
# Start the shot put at 2.0 meters at a projection angle of 
# 37 degrees above horizon at 15 m/s
v0_mp2 = 0.15
ang0_deg = 0.37
ang0_rad = ang0_deg * const.pi / 180.0

# NOTE: POSITIVE value is backspin
w_radpsec = 2.0 * (2.0 * const.pi)  

s0 = [0.0,
      2.0,
      v0_mp2 * math.cos(ang0_rad),
      v0_mp2 * math.sin(ang0_rad)]

t0 = 0.0
dt = 0.01
tstop = 100.0

# Create some arrays for storage so we can plot results later
# and set the initial conditions from the above s0 state
shotput_index = 0
plastic_index = 1
beach_index   = 2

max_index = 3

ts = np.arange(0.0, tstop, dt)
px = np.zeros((len(ts), max_index));
px[0,:] = s0[0]
py = np.zeros((len(ts), max_index));
py[0,:] = s0[1]
vx = np.zeros((len(ts), max_index));
vx[0,:] = s0[2]
vy = np.zeros((len(ts), max_index));
vy[0,:] = s0[3]
qx = np.zeros((len(ts), max_index));
qx[0,:] = q(vx[0,0],rho_kgpm3)
qy = np.zeros((len(ts), max_index));
qy[0,:] = q(vy[0,0],rho_kgpm3)
Fx = np.zeros((len(ts), max_index));
Fx[0,shotput_index] = Fdrag(vx[0,shotput_index],Cd, A_shotput_m2, rho_kgpm3)
Fx[0,plastic_index] = Fdrag(vx[0,plastic_index],Cd, A_plastic_m2, rho_kgpm3)
Fx[0,beach_index]   = Fdrag(vx[0,beach_index],Cd, A_beach_m2, rho_kgpm3)
Fy = np.zeros((len(ts), max_index));
Fy[0,shotput_index] = F(vy[0,shotput_index],Cd, A_shotput_m2, V_shotput_m3, rho_kgpm3)
Fy[0,plastic_index] = F(vy[0,plastic_index],Cd, A_plastic_m2, V_plastic_m3, rho_kgpm3)
Fy[0,beach_index]   = F(vy[0,beach_index],Cd, A_beach_m2, V_beach_m3, rho_kgpm3)


# ****************************************************************
# ****************************************************************
# NOTE: The following two setups and loops could also be in a function
#       to make reuse easier. Save that for another day.
# ****************************************************************
# ****************************************************************

# Create the integrator and initialize it for the shot put
# The dopri5 is a runge-kutta 4th/5th order stepping solution
# We'll explain that some other day

myInt = ode(f).set_integrator('dopri5')
myInt.set_initial_value(s0, t0).set_f_params(Cd, A_shotput_m2, V_shotput_m3, m_shotput_kg, rho_kgpm3, rho_shotput_kgpm3, r_shotput_m, w_radpsec)

# Run the integrator until the shot put hits the ground
# Note: While I like using the variable 's' for state, the integrator
# internally uses 'y' so we will transfer the states to our own storage
# at each step to plot later
i = 1
while myInt.successful() and myInt.t < tstop and myInt.y[1] > 0 and i < len(ts):
    myInt.integrate(myInt.t + dt)
    px[i,shotput_index] = myInt.y[0]
    py[i,shotput_index] = myInt.y[1]
    vx[i,shotput_index] = myInt.y[2]
    vy[i,shotput_index] = myInt.y[3]
    qx[i,shotput_index] = q(vx[i,shotput_index],rho_kgpm3)
    qy[i,shotput_index] = q(vy[i,shotput_index],rho_kgpm3)
    Fx[i,shotput_index] = Fdrag(vx[i,shotput_index],Cd, A_shotput_m2, rho_kgpm3)
    Fy[i,shotput_index] = Fdrag(vy[i,shotput_index],Cd, A_shotput_m2, rho_kgpm3)
    i = i + 1

# Change the parameters to run the integrator on the plastic ball-like object
myInt.set_initial_value(s0, t0).set_f_params(Cd, A_plastic_m2, V_plastic_m3, m_plastic_kg, rho_kgpm3, rho_plastic_kgpm3, r_plastic_m, w_radpsec)

# Run the integrator until the plastic hits the ground
j = 1
while myInt.successful() and myInt.t < tstop and myInt.y[1] > 0 and j < len(ts):
    myInt.integrate(myInt.t + dt)
    px[j,plastic_index] = myInt.y[0]
    py[j,plastic_index] = myInt.y[1]
    vx[j,plastic_index] = myInt.y[2]
    vy[j,plastic_index] = myInt.y[3]
    qx[j,plastic_index] = q(vx[j,plastic_index],rho_kgpm3)
    qy[j,plastic_index] = q(vy[j,plastic_index],rho_kgpm3)
    Fx[j,plastic_index] = Fdrag(vx[j,plastic_index],Cd, A_plastic_m2, rho_kgpm3)
    Fy[j,plastic_index] = Fdrag(vy[j,plastic_index],Cd, A_plastic_m2, rho_kgpm3)
    j = j + 1

# Change the parameters to run the integrator on the beach ball
myInt.set_initial_value(s0, t0).set_f_params(Cd, A_beach_m2, V_beach_m3, m_beach_kg, rho_kgpm3, rho_beach_kgpm3, r_beach_m, w_radpsec)

# Run the integrator until the beach ball hits the ground
k = 1
while myInt.successful() and myInt.t < tstop and myInt.y[1] > 0 and k < len(ts):
    myInt.integrate(myInt.t + dt)
    px[k,beach_index] = myInt.y[0]
    py[k,beach_index] = myInt.y[1]
    vx[k,beach_index] = myInt.y[2]
    vy[k,beach_index] = myInt.y[3]
    qx[k,beach_index] = q(vx[j,beach_index],rho_kgpm3)
    qy[k,beach_index] = q(vy[j,beach_index],rho_kgpm3)
    Fx[k,beach_index] = Fdrag(vx[k,beach_index],Cd, A_beach_m2, rho_kgpm3)
    Fy[k,beach_index] = Fdrag(vy[k,beach_index],Cd, A_beach_m2, rho_kgpm3)
    k = k + 1
    
pl.figure(1)
pl.cla()
pl.grid()
pl.plot(px[0:i,shotput_index],py[0:i,shotput_index],
        px[0:j,plastic_index],py[0:j,plastic_index],
        px[0:k,beach_index],  py[0:k,beach_index])
pl.title('Trajectory')
pl.xlabel('meters')
pl.ylabel('meters')
pl.legend(['Shot Put',
           'plastic',
           'Beach'])

pl.figure(2)
pl.cla()
pl.grid()
pl.plot(ts[0:i],vx[0:i,shotput_index],
        ts[0:i],vy[0:i,shotput_index],
        ts[0:j],vx[0:j,plastic_index],
        ts[0:j],vy[0:j,plastic_index],
        ts[0:k],vx[0:k,beach_index],
        ts[0:k],vy[0:k,beach_index])
pl.title('Speed Components')
pl.xlabel('time (s)')
pl.ylabel('speed (m/s)')
pl.legend(['Shot Put vx',
           'Shot Put vy', 
           'plastic vx', 
           'plastic vy', 
           'Beach vx', 
           'Beach vy'])

pl.figure(3)
pl.cla()
pl.grid()
pl.plot(ts[0:i],Fx[0:i,shotput_index],
        ts[0:i],Fy[0:i,shotput_index],
        ts[0:j],Fx[0:j,plastic_index],
        ts[0:j],Fy[0:j,plastic_index],
        ts[0:k],Fx[0:k,beach_index],
        ts[0:k],Fy[0:k,beach_index])
pl.title('Drag Components')
pl.xlabel('time (s)')
pl.ylabel('drag (N)')
pl.legend(['Shot Put Fx',
           'Shot Put Fy', 
           'plastic Fx', 
           'plastic Fy',
           'Beach Fx', 
           'Beach Fy'])
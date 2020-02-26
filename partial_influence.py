# -*- coding: utf-8 -*-
"""
partial influence demonstrates the partial impact of base and exponents

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

def dfdb(B, E):
    """
    B is the base
    E is the exponent
    f = B^E
    partial df/dB = E * B**(E-1)    
    """
    out = E * (B**(E-1))
    return out

def dfde(B, E):
    """
    B is the base
    E is the exponent
    f = B^E
    partial df/dE = B**(E) * ln(B)        
    """
    out = (B**E) * np.log(B)
    return out    
    
plot.figure(1)
plot.cla()
plot.grid()

x = 5
Bs = np.arange(-x,+x,0.5)     # Start, Stop, Step
Es = np.arange(-x,+x,0.5)

# For each E held constant
for E in Es:
    plot.plot(Bs,dfdb(Bs,E))

plot.figure(2)
plot.cla()
plot.grid()

# For each B help constant
for B in Bs:
    plot.plot(Es,dfde(B,Es))

plot.show()

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 19:23:36 2017

@author: mtkes
"""

import Astro
import numpy as np

# Stack the data tx1x9, which is easy for people to read
# sequence (or time) goes down the page and each row
# of numbers is the DCM value for each point in the sequence
# The interpretation is either rows or columns and can be
# specified at construction


phi = np.arange(0,np.pi,0.1).transpose()

zeros = np.zeros(phi.shape)
ones = np.ones(phi.shape)

theta = zeros
psi = zeros

ax = np.array([ones,  zeros,       zeros, 
               zeros, np.cos(phi), -np.sin(phi), 
               zeros, np.sin(phi), np.cos(phi)])

A = Astro.dcm(ax[:,np.newaxis,...].transpose())

q = Astro.quaternion(A)

x = [[[1,2,3,4,5,6,7,8,9]],
     [[11,12,13,14,15,16,17,18,19]]]

d1 = Astro.dcm(x) #NOTE: Normalized data is NOT checked at this time

print(d1)

d2 = Astro.dcm(x,direction='columns')

print(d2)

print("...")
print(d1[:,:,0])
print("... d1 * d1")
d3 = np.matmul(d1,d1)

print(d3)

d = d1[0,:,:]
print('d is ')
print(d)

print('d * d1...')
d4 = np.matmul(d,d1)
print(d4)

print('d1 * d...')
d5 = np.matmul(d1, d)
print(d5)

print('d * d1... overload')
d6 = d*d1
print(d6)

print('d1 * d... overload')
d7 = d1*d
print(d7)

print("q...")
print(q)





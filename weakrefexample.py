# -*- coding: utf-8 -*-
"""
Created on Thu May 26 07:09:17 2016

@author: mtkessel
"""

import weakref

class A(object):
    def __init__(self, aData):
        print("A " + str(aData) + " created")
        self.data = aData
        
    def display(self):
        print("A = " + self.data)

    def __del__(self):
        print("A " + str(self.data) + " deleted")


class B(object):
    def __init__(self, aData, aS):
        print("B " + str(aData) + " created")
        self.data = aData
        self.s = aS #weakref.ref(aS)
        
    def display(self):
        print("B = " + self.data)

    def __del__(self):
        print("B " + str(self.data) + " deleted")
        
class C(A):
    def __init__(self, aData):
        print("C " + str(aData) + " created")
        A.__init__(self,aData)
        self.someB = weakref.ref(B(2,self))
        
    def display(self):
        print("C = " + self.data)
        
    def __del__(self):
        A.__del__(self)
        print("C " + str(self.data) + " deleted")
        
c = C(1)
c = []
    
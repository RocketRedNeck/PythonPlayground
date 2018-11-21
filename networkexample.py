#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
networkexample

Quick example of using network tables

Copyright (c) 2017 - the.RocketRedNeck@gmail.com

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

# import the necessary packages

import time

# use pip install pynetworktables or --update or --user as necessary
from networktables import NetworkTables

import logging      # Needed if we want to see debug messages from NetworkTables

# import our classes

# Address for NetworkTable server
#networkTableServerAddress = '127.0.0.1'  # Loopback
#networkTableServerAddress = '10.41.83.2' # Rio On competition field
#networkTableServerAddress = '10.38.14.2' # Rio On practice field
networkTableServerAddress = '192.168.0.103' # At 'home'

# And so it begins
print("Starting Network Example!")

# To see messages from networktables, you must setup logging
logging.basicConfig(level=logging.DEBUG)

try:
    NetworkTables.initialize(server=networkTableServerAddress)
    
except ValueError as e:
    print(e)
    print("\n\n[WARNING]: NetworkTable Not Connected!\n\n")

bvTable = NetworkTables.getTable("ExampleTable")
bvTable.putString("ExampleTable","Starting")

bvTable.putString("ExampleTable","ONLINE")

runTime = 0
bvTable.putNumber("ExampleTime",runTime)
nextTime = time.time() + 1

try:
	while (True):

		if (time.time() > nextTime):
			nextTime = nextTime + 1
			runTime = runTime + 1
			bvTable.putNumber("ExampleTime",runTime)
			
		time.sleep(0.1)
except KeyboardInterrupt as e:
	bvTable.putString("ExampleTable","offline")
	time.sleep(0.250)
	
print("Goodbye!")


# -*- coding: utf-8 -*-
"""
UDP Client Example

Copyright (c) 2017 - Michael Kessel (mailto: the.rocketredneck@gmail.com)
a.k.a. RocketRedNeck, RocketRedNeck.com, RocketRedNeck.net 

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

import socket

IP_ANY = ''
IP_LOOPBACK = '127.0.0.1'
IP_LOCAL = IP_ANY # use the first interface we can find (use IP_LOOPBACK if you don't want to use a physical interface)

# We must know this port number or negotiate it on another well known port
# to receive data
PORT = 53421

while (True):
    mySocket  = socket.socket(family=socket.AF_INET,
                                     type=socket.SOCK_DGRAM,
                                     proto=socket.IPPROTO_UDP)
    
    if (mySocket == None):
        print("Unable to create listen socket")
        break
    
    print("Waiting for server...")
    
    mySocket.bind((IP_ANY, PORT)) # We'll use any interface that is on this machine
    
    
    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    mySocket.settimeout(0.2)
    
    timeoutCount= 0
    while (True):
        try:
            data = mySocket.recv(1024)
            timeoutCount = 0
            data = data.decode("utf-8")
            print(data + "!")
            if (data == ''):
                break
        except socket.timeout:
            timeoutCount = timeoutCount + 1
            print("Timeout " + str(timeoutCount))
        except Exception as e:
            print(e)
            break
    
    
        
    
    
            
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:00:46 2017

@author: mtkes
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
    
    
        
    
    
            
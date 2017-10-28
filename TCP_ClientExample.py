# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:00:46 2017

@author: mtkes
"""

import socket
import time

IP_LOOPBACK = '127.0.0.1'
PORT = 53421

while (True):
    connectionSocket  = socket.socket(family=socket.AF_INET,
                                     type=socket.SOCK_STREAM,
                                     proto=socket.IPPROTO_TCP)
    
    if (connectionSocket == None):
        print("Unable to create listen socket")
        break
    
    print("Waiting for server...")
    
    try:
        connectionSocket.connect((IP_LOOPBACK, PORT))
        connectionSocket.settimeout(5.0)
        
        print("Connected!")
        
        connectionSocket.send(b'Go')
        
        while (True):
            try:
                data = connectionSocket.recv(1024)
                data = data.decode("utf-8")
                print(data + "!")
                if (data == ''):
                    break
            except socket.timeout:
                print("Timeout...")
            except Exception as e:
                print(e)
                break
                
    except Exception as e:
        print(e)

    connectionSocket.close()
    
    
        
    
    
            
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 14:00:46 2017

@author: mtkes
"""

import socket
import struct

IP_ANY = ''
IP_LOOPBACK = '127.0.0.1'
IP_LOCAL = IP_ANY

IP_MULTICAST_GROUP_A = '230.0.0.1'

PORT = 53421

while (True):
    mySocket  = socket.socket(family=socket.AF_INET,
                                     type=socket.SOCK_DGRAM,
                                     proto=socket.IPPROTO_UDP)
    
    if (mySocket == None):
        print("Unable to create listen socket")
        break
    
    print("Waiting for server...")
    mySocket.bind((IP_LOCAL, PORT))    # We only receive on this port
    
    # Now we need to join the group
    # Joining the group allows us to receive data without the sender
    # knowing our interface address
    group = socket.inet_aton(IP_MULTICAST_GROUP_A)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)    
     
    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    mySocket.settimeout(0.2)
    
    timeoutCount= 0
    
    while (True):
        try:
            data = mySocket.recv(1024)
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
    
    
        
    
    
            
# -*- coding: utf-8 -*-
"""
UDP Multicast Client Example

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
import struct

IP_ANY = ''
IP_LOOPBACK = '127.0.0.1'
IP_LOCAL = IP_ANY

IP_MULTICAST_GROUP_A = '230.0.0.1'

PORT = 54321

while (True):
    mySocket  = socket.socket(family=socket.AF_INET,
                                     type=socket.SOCK_DGRAM,
                                     proto=socket.IPPROTO_UDP)
    
    if (mySocket == None):
        print("Unable to create listen socket")
        break
    
    # Allow the address/port pair to be reused by other processes
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
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
    
    
        
    
    
            
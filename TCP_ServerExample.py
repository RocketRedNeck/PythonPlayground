# -*- coding: utf-8 -*-
"""
TCP Server Example

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

# IP Addresses are used by the network hardware to route traffic
# It is just like having a house address or zip code
# In networks the interface hardware is assigned an IP address to
# make the interface unique within the network.
# In the IPv4 standard IP addresses contain 4 bytes representing
# layers to the local network. Usually, the address is represented
# as a string containing '.' as a delimeter for readability
#
# Examples:
#   Some addresses are special, defined in various standards to mean
#   specific things to the network (https://en.wikipedia.org/wiki/Reserved_IP_addresses)
#
#   The standard loopback address (talk to self) is '127.0.0.1'
#
#   A typical Ethernet router (gateway) at '192.168.0.1' will assign your 
#   PC something like '192.168.0.2', '192.168.0.3', etc. although sometimes the
#   '10.x,x,x' range is used.
##
#   '255.255.255.255' is reserved to broadcast to all nodes on the network
#
#   '224.0.0.0' to '239.255.255.255' is reserved for multicast
#
IP_ANY = ''     # In this case we don't care what address our hardware has
IP_LOOPBACK = '127.0.0.1'
IP_LOCAL = IP_ANY

# Ports are a way of distinguishing the type of information traffic on a
# netowrk. The port is simply a logical distinction that allows traffic to
# be routed to one or more sockets that care about the information.
#
# Like IP Addressses, some ports are reserved (https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers)
# and should not be arbitrarily used for other purposes as this could create
# confusion in the applications that are expecting the traffic.
#
# 0 to 1023 are "well known"
# 1024 to 49151 are "registered"
# 49152 to 65535 are "dynamic" and may be assigned by user applications
#
# We just need to pick a port to start listening for connections
# then we will let the system assign connections to a new port to
# keep traffic separated
PORT = 53421

while (True):
    # A listening socket is an object we will use to listen for
    # requests for service
    listeningSocket = socket.socket(family=socket.AF_INET,
                                 type=socket.SOCK_STREAM, 
                                 proto=socket.IPPROTO_TCP)
    
    if (listeningSocket == None):
        print("Unable to create listen socket")
        break
    
    # Allow the address/port pair to be reused by other processes
    listeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 'binding' a socket just means associating it with an
    # interface address and a port on that address with the socket
    # object. All network traffic to the address and port will signal
    # the socket each time a message comes in.
    # The interface address can be a specific IP address associated
    # with network interface hardware or we can request that the
    # first interface found is used (IP_ANY). In some environments
    # IP_ANY is '0.0.0.0', in this environment the empty string has
    # the same effect.
    #
    # Ports are a way of identifying packets to be routed to specific
    # user path on an interface
    print("Binding...")
    listeningSocket.bind((IP_LOCAL, PORT))
    
    # Now we set up listening to wait for a connection request
    # We set the backlog to 0 to allow up to 0 unaccepted connection
    # before replying with a "refuse".
    # We can set the backlog larger to allow the requests to come in
    # slightly faster than we can accept, but in general the lower
    # value just makes the client ask again until we can get around
    # to the request.
    print("Listen...")
    listeningSocket.listen(0)
    
    listeningSocket.settimeout(1.0)

    try:   
        acceptedSocket, addressInfo = listeningSocket.accept()
        print("Accepted connection @ " + str(addressInfo[0]) + " : " + str(addressInfo[1]))
        
        listeningSocket.close() # For this example we don't need this
        
        acceptedSocket.settimeout(1.0)
        data = acceptedSocket.recv(1024)
        if not data:
            raise Exception("Socket Receive Failure")
            
        data = data.decode("utf-8")
        print('Command = ' + data)
        sendOk = True
        if (data == 'Go'):
            print("Serving...")
            i = 0;
            while (True):
                try:
                    i = i + 1
                    
                    # Because we are sending into a stream it
                    # is up to us to define where the "message" or
                    # data boundaries are... in this simple exmaple
                    # we just use '*' to identify the end of our "message"
                    # This allows the client to dice up the data on some
                    # boundry as it receives the stream
                    s = 'String = ' + str(i + 1) + '*'
                    print(s)
                    acceptedSocket.send(str.encode(s))
                except Exception as e:
                    print(e)
                    sendOk= False
                    break
                if (sendOk == False):
                    break
        else:
            print("Invalid Command Received By Server")
        
        print("Closing Service...")       
        acceptedSocket.close()
    except socket.timeout:
        print("Server Detected Timeout")
    except Exception as e:
        print(e)
        
    
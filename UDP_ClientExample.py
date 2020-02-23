# -*- coding: utf-8 -*-
"""
UDP Client Example - RocketRedNeck's guide for highschool students and anyone
curious about using sockets for connectionless communication between two points.

NOTE: There are more comments in here than code, hopefully to explain why and
how things are working the way they are.

The terms "client" and "server" do not specifically mean anything more than
one side of a communication wants information or service  and the other side 
will provide it. Both sides of a client/server relationship can send and 
receive data. The formality of the relationship will determine how the 
connection is maintained and what type of information is exchanged.

In this simple example the server will send a continuous sequence of data and
the client will receive the data sequence. The server can start and stop sending
the data any time it wants and does not require that the client be receiving.
The client can start or stop receiving the data any time it wants and does
not require that the server be sending information; however, the client will
operate on a timeout condition to allow it to check other status or exit
conditions as needed.

Since there is no need for a guarantee of a connection between to two ends we
define this relationship as "connectionless" and will use the User Datagram
Protocol (UDP) for our sockets. UDP provides a simple mechanism to move data
between a sender and a receiver, requiring that the sender know nothing more
than the location (address and port) of the receiver. The client does not need
to know anything about server location, and only needs to open a port on a
local interface, which we discuss in the code/comments below.

Running:
    More or less...
    Start a terminal and invoke 'python ./UDP_ClientExample.py'
    In a separate terminal invoke 'python ./UDP_ServerExample.py'
    
    Use ctrl-s (pause) ctrl-q (resume) to pause/resume terminal
    Use ctrl-c (break) or equivalent to stop either side
    
    The client socket should continue to receive while display is paused and
    will the client will process any socket backlog when resumed
    The client should indicate timeout when the server pauses or is stopped

******************************************************************************
******************************************************************************
******************************************************************************

Copyright (c) 2020 - Michael Kessel (mailto: the.rocketredneck@gmail.com)
a.k.a. RocketRedneck, RockyRed, or the Dude With a Bag of Chips

RocketRedNeck and MIT Licenses 

RocketRedNeck hereby grants license for others to copy and modify this source 
code for whatever purpose other's deem worthy as long as RocketRedNeck is given
credit where where credit is due and you leave RocketRedNeck out of it for all
other nefarious purposes. 

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

******************************************************************************
******************************************************************************
******************************************************************************
"""
import argparse
parser = argparse.ArgumentParser(description='UDP Client Example')
parser.add_argument('--addr', 
                    default='0.0.0.0',
                    type=str, 
                    help='Interface Address (default=0.0.0.0 "any")')
parser.add_argument('--port',
                    default=53431,
                    type=int, 
                    help='Receiving Port (default=54321')
args = parser.parse_args()

# "Sockets" are the interface developed in the mists of history to connect two
# points of a communication exchange. You can find a socket implementation in
# just about every system-level language (like C, C++, C#, java, python, etc.)
#
# While the API (application programming interface) will vary between
# implementations (Microsoft, Linux, VxWorks, for example all differ), 
# the basic concepts are the same.
#   1. import or include your socket interface
#   2. instantiate a socket with the family, type, and protocol you need
#   3. configure any special options
#   4. send/receive using the steps required for the selected protocol

import socket

# As discussed above, sending requires an address and port number in order to 
# send information to the receiver. The receiver needs an address of its own 
# interface (the network interface controller, NIC) and the port number it
# wants to receive on.

# So a few words about the Internet Protocol (IP) Address
#
# IP Addresses are used by the network hardware to route traffic
# It is just like having a house address or zip code
# In networks the interface hardware is assigned an IP address to make the 
# interface unique within the network.
# In the IPv4 standard IP addresses contain 4 bytes representing
# layers to the local network. Usually, the address is represented as a string
# containing '.' as a delimeter for readability
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
#
#   '255.255.255.255' is reserved to broadcast to all nodes on the network
#
#   '224.0.0.0' to '239.255.255.255' is reserved for multicast, something we
#   will discuss later, in a different example.
#

IP_BIND_ADDRESS = args.addr         # The interface I want to bind with for this demo

# So a few words about ports.
#
# Ports are a way of separating the context (meaning and purpose) of transactions
# arriving at the IP Address. Ports are like having rooms in a house, where each
# room exists for a different purpose.
#
# A port is just a number from 0 to 65535. We must know this port number or 
# negotiate it on another well known port to receive data. Some port numbers
# have specific meaning, and are 'officially' assigned by IANA as described
# in the article at https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
#
# 0 to 1023 are "well known"
# 1024 to 49151 are "registered"
# 49152 to 65535 are "dynamic" and may be assigned by user applications
#
# The port you use for an application can be negotiated, configured at initialization
# or even just picked from values not used on your system. There are numerous
# ways to query your system to determine which ports are open, but those details
# will not be discussed here
#
# We just need to pick a port to keep traffic separated for our purposes

PORT = args.port                    # Just a number I know is not being used
                                    # on this machine.

# To make this 'application' robust we desire that the communication keep trying
# no matter some internal problem. For this reason there are two loops below.
#
# The outer loop creates the socket, binds it to the address:port we want, and
# then enters the inner loop. Unhandled errors in the inner loop will re-enter
# the outer loop to attempt recreating a socket bound to the same point.
#
# The inner loop will call the socket receiving function (recv); this call will
# block unless we tell it not to; blocking means that the call will not exit
# until either a message has arrived or a timeout has occured.
#
# Each time the recv function returns we have the opportunity to check if it
# returned with data or timed out (which we handle as an exception); all other
# exceptions are treated as a serious error causing the code the re-enter the
# outer loop to re-create the socket.

while (True):
    # Create the socket to use the family, type and protocol we need
    #
    # Family - (Address Family, AF) the AF identifies how addresses should be
    #           translated. For our purposes they are
    #               AF_INET  IPv4 meaning 4 bytes 0xAABBCCDD or 'aaa.bbb.ccc.ddd'
    #               AF_INET6 IPc6 meaning a 6 byte address (because there
    #                        are more than 4 billion devices in the world)
    #               AF_UNIX  are Unix Domain Sockets (UDS) allowing passing of
    #                        information between unix processes via the file system
    #                        The address is a file name
    #
    # Type - SOCK_STREAM    A stream socket provides bidirectional, reliable, 
    #                       sequenced, and unduplicated flow of data with no 
    #                       record boundaries. After the connection has been 
    #                       established, data can be read from and written to 
    #                       these sockets as a byte stream.
    #                       The 'beginning' and 'end' of information segments in
    #                       stream will need to be delimined by the designer.
    #                       Often TCP streams are the basis of other protocols like
    #                       HTTP, FTP, etc where the delimiters are pulled from
    #                       the TCP stream; many socket interfaces will default the
    #                       socket protocol to TCP when indicating the socket is 
    #                       streaming.
    #        SOCK_DGRAM     A datagram socket supports bidirectional flow of 
    #                       messages. A process on a datagram socket can receive
    #                       messages in a different order from the sending 
    #                       sequence and can receive duplicate messages. Record
    #                       boundaries in the data are preserved. 
    #                       Datagrams can be as big as about 64 KB but any that
    #                       are larger than the MTU (Maximum Transmission Unit, 
    #                       typical is 1500 bytes) along the network path will 
    #                       be fragmented, which could cause messages to be lost.
    #                       Using STREAM if ordering and reliability are needed.
    #                       Use DGRAM if your application is tolerant to ordering,
    #                       dropped, and duplicated messages; which is usually
    #                       handled by the message content.
    #        SOCK_RAW       RAW provides access to ICMP (Internet Control Message
    #                       Protocol). These sockets are normally datagram oriented, 
    #                       although their exact characteristics are dependent 
    #                       on the interface provided by the protocol. 
    #                       Raw sockets are not for most applications. They are 
    #                       provided to support developing new communication 
    #                       protocols or for access to more esoteric facilities
    #                       of an existing protocol. Only superuser processes 
    #                       can use raw sockets.
    
    mySocket  = socket.socket(family=socket.AF_INET,
                                     type=socket.SOCK_DGRAM,
                                     proto=socket.IPPROTO_UDP)
    
    if (mySocket == None):
        print("Unable to create DGRAM socket")
        break
        
    # 'binding' a receiving socket just means associating it with an interface
    # address and a port with the socket object.
    # All network traffic to the address and port will signal the socket each 
    # time a message comes in (because we are using DGRAM as the type in this 
    # example.
    #
    # While a socket can both send and receive, it is often useful to simply
    # create seaparate sender/receiver threads (or processes) and pass multiple
    # communication needs through some form of queue.
    #
    # Ocassionally using the same socket for sending/receiving may cause other
    # underlying problems deep in the OS that can be corrected through changes
    # so caution is warranted.
    # 
    #
    # So what address and port should be bind?
    #
    # The interface address can be a specific IP address associated with network
    # interface hardware or we can request that any available interface be used.
    # The port is any available port that both sides can agree upon.
    # See the discussion of address and ports, above, for more information.
    # user path on an interface
    
    print("Binding to IP = '" + IP_BIND_ADDRESS + "' on PORT = " + str(PORT))
    
    # Allow the address/port pair to be reused by other processes
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    mySocket.bind((IP_BIND_ADDRESS, PORT))
        
    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data. Without this the socket will block 'forever' and
    # stopping the process by simple commands becomes difficult, usually
    # requiring that the process be killed.
    #
    # Python timeout settings are simple, while other environments require
    # the use of the socket options interface (setsockopt). See the C++ example
    # for more information.
    mySocket.settimeout(0.2)
    
    timeoutCount= 0
    while (True):
        try:
            data, address = mySocket.recvfrom(1024)
            timeoutCount = 0
            
            # In order to print the data out in Python we need to decode
            # the bytes into a string (otherwise the b'string' will display)
            data = data.decode("utf-8")
            print(data + " <----- " + str(address[0]) + ":" + str(address[1]))
            if (data == ''):
                break
        except socket.timeout:
            timeoutCount = timeoutCount + 1
            print("Timeout " + str(timeoutCount))
        except Exception as e:
            print(e)
            break
    
    
        
    
    
            
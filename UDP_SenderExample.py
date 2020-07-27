# -*- coding: utf-8 -*-
"""
UDP Server Example - RocketRedNeck's guide for highschool students and anyone
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
import time

default_ipaddr = '127.0.0.1'  # Loopback
default_port = 54321
default_pktsize = 32*1024

parser = argparse.ArgumentParser(description='UDP Sender Example')
parser.add_argument('--addr', 
                    default=default_ipaddr,
                    type=str, 
                    help=f'Destination Address (default={default_ipaddr})')
parser.add_argument('--port',
                    default=default_port,
                    type=int, 
                    help=f'Destination Port (default={default_port}')
parser.add_argument('--pktsize',
                    default=default_pktsize,
                    type=int, 
                    help=f'Packet Size (default={default_pktsize})')
parser.add_argument('--delay',
                    default=0,
                    type=float, 
                    help=f'delay (busy wait) between sending frames (default = 0)')
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
#   The standard 'any" address is '0.0.0.0' and used only for receiver binding
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

IP_DEST_ADDRESS = args.addr     # The interface I want to send to for this demo

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

DEST_PORT = args.port               # Just a number I know is not being used
                                    # on this machine.

# To make this 'application' robust we desire that the communication keep trying
# no matter some internal problem. For this reason there are two loops below.
#
# The outer loop creates the socket, and then enters the inner loop. Unhandled
# errors in the inner loop will re-enter the outer loop to attempt recreating a
# socket of the same type.
#
# The inner loop will call the socket sending function (sendto) regardless if
# there is anyone listenting at the indicated destination.

while (True):
    # A UDP socket is an object we will use to send data to an address
    mySocket = socket.socket(family=socket.AF_INET,
                             type=socket.SOCK_DGRAM, 
                             proto=socket.IPPROTO_UDP)
    
    if (mySocket == None):
        print("Unable to create DGRAM socket")
        break
    
    # Sending messages via a DGRAM socket (UDP) is simpler than receiving.
    # While the receiver needs to (explicitly or implicitly) bind the socket
    # to an interface and port the sender simply needs to send to the desired
    # address and port. The trick here is that the sender must be made aware
    # of the destination address and port, either by requirement or some
    # programmatics means like initialization files or a separate broadcast
    # or multicast negotiation. Such techniques will not be discussed here.
    #
    # In this example, it is sufficient to specify the destination address
    # and port at the point we need to send the data.
       
    # Now we just start sending
    print("Sending...")

    i = 0
    starttime_sec = time.time()
    lasttime_sec = starttime_sec
    nexttime_sec = starttime_sec + 1.0
    lasti = 0
    avgips = 0.0
    while (True):
        try:
            i = i + 1
            
            display = False

            now_sec = time.time()
            if (now_sec >= nexttime_sec):
                nexttime_sec += 1.0
                
                dt = now_sec - lasttime_sec
                lasttime_sec = now_sec
                if (dt > 0.0):
                    avgips = float(i - lasti)/dt
                else:
                    avgips = 0.0
                lasti = i
                display = True
                    
            sn = str(i+1)

            if display:
                print(f'----> {IP_DEST_ADDRESS}:{DEST_PORT} = {sn} ({avgips:6.0f} Hz) ({(args.pktsize*avgips)/1024/1024:7.3f} MBps)')

            # Python requires a little bit of endcode/decode logic to ensure
            # that only the data bytes are sent
            sn += (args.pktsize - len(sn)) * '*'
            sn = sn.encode("utf-8")
            mySocket.sendto(sn, (IP_DEST_ADDRESS, DEST_PORT))
            if args.delay > 0:
                now_sec = time.perf_counter()
                while (time.perf_counter() - now_sec < args.delay):
                    now_sec = now_sec
            
        except Exception as e:
            print(e)
            sendOk= False
            break

        
    
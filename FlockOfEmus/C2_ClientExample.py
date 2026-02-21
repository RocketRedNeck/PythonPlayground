# -*- coding: utf-8 -*-
"""
TCP Client Example

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
import argparse
import socket
import time

default_ipaddr = '127.0.0.1'  # loopback
default_port = 54321
default_rcvsize = 48*1024

parser = argparse.ArgumentParser(description='UDP Receiver Example')
parser.add_argument('--addr', 
                    default=default_ipaddr,
                    type=str, 
                    help=f'Interface Address (default={default_ipaddr})')
parser.add_argument('--port',
                    default=default_port,
                    type=int, 
                    help=f'Receiving Port (default={default_port})')
parser.add_argument('--size',
                    default=default_rcvsize,
					type=int,
					help=f'Socket Receive Size (default={default_rcvsize})')
parser.add_argument('--delay',
                    default=0,
                    type=float, 
                    help=f'delay (busy wait) every --delaymod frames (default = 0)')
parser.add_argument('--delaymod',
                    default=1,
                    type=int, 
                    help=f'modulo when to apply --delay when delay > 0 (default = 1)')

args = parser.parse_args()

IF_ADDR = args.addr
PORT = args.port

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

done = False

constart_sec = time.time()
contime_sec = constart_sec
conerrtime_sec = contime_sec

try:
    print(f"Starting TCP Client Example @ {IF_ADDR}:{PORT}...")
    while (not done):
        connectionSocket  = socket.socket(family=socket.AF_INET,
                                        type=socket.SOCK_STREAM,
                                        proto=socket.IPPROTO_TCP)
        
        if (connectionSocket == None):
            print("Unable to create listen socket")
            break
        
        if (time.time() > contime_sec):
            print(f"@ T+{time.time() - constart_sec:.0f} Attempting to connect to server...", end='\r', flush=True)
            contime_sec = time.time() + 1.0
        
        try:        
            connectionSocket.settimeout(1.0)
            connectionSocket.connect((IF_ADDR, PORT))
            #connectionSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.size)
            #print(connectionSocket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
            
            print("\nConnected!")
            
            connectionSocket.send(b'Go')
            
            prefix_data = ''
            count = 0
            lostcount = 0

            starttime_sec = time.time()
            lasttime_sec = starttime_sec
            nexttime_sec = starttime_sec + 1.0
            lastcount = 0
            avgips = 0.0
            lasttermtime_sec = 0.0

            display = False
            
            while (not done):
                try:
                    data = connectionSocket.recv(args.size)
                    data = prefix_data + data.decode("utf-8")
                    if (data == ''):
                        break
                    
                    # because the data is a stream of information
                    # we must parse it outselves
                    # In this example we are using the '*' character
                    # as a delimiter
                    terminators = find(data,'*')

                    # If the last byte is not '*' then we need to hold
                    # the remaining data for prepending the next part
                    # of the stream
                    if terminators != []:
                        lasttermtime_sec = time.time()
                        if data[-1] != '*':
                            # Strip trailing data for next receive frame
                            prefix_data = data[terminators[-1]+1:]
                            data = data[:terminators[-1]+1]

                        starts = [0] + [x+1 for x in terminators[:-1]]
                        for i in range(len(starts)):
                            bang = data[starts[i]:].find('!')
                            msg = data[starts[i]:starts[i]+bang]
                            if (msg == ''):
                                break
                            gt = msg.find('<')
                            sn = int(msg[:gt])
                            count = count + 1

                            now_sec = time.time()
                            if (now_sec >= nexttime_sec):
                                nexttime_sec += 1.0
                                
                                dt = now_sec - lasttime_sec
                                lasttime_sec = now_sec
                                if (dt > 0.0):
                                    avgips = float(count - lastcount)/dt
                                else:
                                    avgips = 0.0
                                lastcount = count

                                display = True

                            if count == 1:
                                lastsn = sn
                            elif lastsn != sn - 1:
                                #print("    SKIP DETECTED!!!")
                                lostcount += (sn - lastsn - 1)

                            if display:
                                display = False
                                print(f'{sn} <-----  : lost = {lostcount} ({100*lostcount/sn:3.0f} %) : ({avgips:6.0f} Hz)')
                            lastsn = sn
                    else:
                        if (time.time() - lasttermtime_sec >= 1.0):
                            print("Timeout...")
                            break
                        else:
                            # Keep waiting for more data until terminator seen (indicating we have a complete 'message')
                            prefix_data = data
                        
                except socket.timeout:
                    print("Timeout...")
                except KeyboardInterrupt:
                    print("Keyboard Interrupt Detected, Stopping Client...")
                    done = True
                    break
                except Exception as e:
                    print(e)
                    break
        except ConnectionRefusedError:
            if (time.time() >= conerrtime_sec):
                conerrtime_sec = time.time() + 1.0
        except KeyboardInterrupt:
            print("Keyboard Interrupt Detected, Stopping Client...")
            done = True
            break                
        except Exception as e:
            print(e)

        connectionSocket.close()
except KeyboardInterrupt:
    print("Keyboard Interrupt Detected, Stopping Client...")
except Exception as e:
    print(e)
    
    
        
    
    
            
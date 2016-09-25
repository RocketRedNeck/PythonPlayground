# -*- coding: utf-8 -*-
"""
Created on Wed May 25 15:37:43 2016

@author: mtkessel
"""

import queue as Q
import serial
import threading
import time
import weakref

class LLAP(serial.Serial):
    """Lightweight Local Automation Protocol (LLAP) defines a small device
       protocol that balances simplicity and human readability. The
       class instance provides either client (commander) or server
       (device) context associated with a specific serial port.
       The object maintains the synchronization and strips the
       protocol syntax from the command/response strings.
       
       A single instance may be used to communicate with multiple devices
       or multiple instance may be defined; each instance of LLAP maintains
       an independent Thread and Queue
    """
    
    def __init__(self,
                 deviceId = '--',
                 *args,
                 **kwargs# whatever args serial wants, serial gets but don't list them here in case base class changes (not our problem!)
                 ):
        """Initialize comm port object. If a port is given, then the port will be
           opened immediately. Otherwise a Serial port object in closed state
           is returned."""
        print(*args)
        self.__running = False
        self.__deviceName = ''
        self.__messageReceived = False
        self.__deviceId = deviceId[:2]
        self.__thread = []
        self.__queue = Q.Queue(1000)
        
        serial.Serial.__init__(self,*args,**kwargs)
        if (self.timeout == None):
            self.timeout = 1.0
        
    def start(self):
        """Start the underlying thread that reads and queues messages
           on this LLAP port
        """
        # NOTE: A weakref.proxy(self) still allows the thread to start correctly
        # (i.e., callable object) but still does not release the referece sufficiently
        # to allow the destructor to actually run
        self.__thread = threading.Thread(target = weakref.proxy(self), name = "Thread_" + self.port)
        self.__thread.start()

    def stop(self, isDestructor = False):
        """Stop the underlying thread that reads and queues messages
           on this LLAP port
        """
        # Stop the thread by setting a flag and joining
        # When the join exits we can test whether the thread
        # really died
        self.__running = False
        if (self.__thread != []):
            print("LLAP Attempting to Stop " + self.__thread.name)
            self.__thread.join(3.0)
            if (self.__thread.is_alive()):
                print("ERROR: LLAP Thread Did NOT Stop")
            else:
                print("LLAP " + self.__thread.name + " Stopped")
                self.__thread = []
        else:
            if (False == isDestructor):
                print("LLAP is already Stopped")
        
    def __del__(self):
        """
        """
        # WARNING: Destructor is NOT guaranteed to execute immediately
        # but placing a stop here ensures that we attempt to stop the
        # thread, but only if we have broken the circular reference
        # induced by passing the callable self to the Thread; making
        # the callable a separate function does not solve the problem
        # because we would still need to pass self as an argument, which
        # holds the reference that prevents the garbage collector from
        # running the destructor.
        self.stop(True) # inidicate that this stop is coming from a destructor
            
    def __call__(self):
        """
        """
        self.__running = True
        print("LLAP " + self.__thread.name + " Started")
        while (self.__running == True):
            c = self.read(1);
            try:
                d = c.decode("utf-8")
                if (d == 'a'):
                    # Found a message start, read the remaining characters
                    # and move them to the message queue
                    c = self.read(11)
                    
                    if (self.__queue.full() == True):
                        self.__queue.get()  # pop oldest item off first
                    
                    m = c.decode("utf-8")
                    print(m)
                    self.__queue.put(m)
                    
                elif (d == 'n'):
                    # Found an Extended message, read it until the requisite EOF/EOL signal 
                    c = self.readline()
                    
                    if (c != -1):
                        # Throw out any trailing control characters (e.g., <CR><LR> or anything else)
                        if (c[-1] <= 32):
                            c = c[:c.__len__()-1]
                            
                        if (c[-1] <= 32):
                            c = c[:c.__len__()-1]
                            
                        if (self.__queue.full() == True):
                            self.__queue.get()  # pop oldest item off first
                            
                        m = c.decode("utf-8")
                        print(m)
                        self.__queue.put(m)
                else:
                    # We are out of sync with the message header
                    # or we timed out, just move on
                    pass
            except:
                pass
            
        print("LLAP " + self.__thread.name + " Stopping...")
    
    def get(self, block = True, timeout_sec = None):
        """
        """
        deviceId = None
        message = None
        
        if (timeout_sec == None):
            timeout_sec = self.timeout
            
        try:
            c = self.__queue.get(block = block, timeout = timeout_sec)
            deviceId = c[0:2]
            message = c[2:]
        except (Q.Empty):
            pass
        
        return message, deviceId
        
    def waitFor(self, message, deviceId=None, timeout=None, displayAll=False):
        """Wait for the specified message as a prefix to any recieved message
           If the incoming message begins with the specified message the wait
           exits, otherwise the specified timeout will be used
           Default timeout applies when no timeout is specified
        """

        if (deviceId == None):
            deviceId = self.__deviceId

        if (timeout == None):
            timeout = self.timeout
            
        currentMessage = None
        currentId = None
        
        startTime = time.time()
        currentTime = startTime
        while ((currentTime - startTime) < timeout):
            currentMessage, currentId = self.get()
            if (True == displayAll):
                self.display(currentMessage, currentId)
                
            if (currentMessage != None):
                if (message == currentMessage[:len(message)]) and (deviceId == currentId):
                    break;
                else:
                    currentMessage = None
                    currentId = None
            currentTime = time.time()
        
        return currentMessage, currentId
                
            
        
    def send(self,message,deviceId=None):
        """
        """
        if (deviceId == None):
            deviceId = self.__deviceId
            
        l = len(message)
        if (l < 9):
            message = message + (9-l)*'-'
            
        message = "a" + deviceId + message + "\r\n"
        self.write(message.encode())

    def display(self,message,deviceId=None):
        """
        """
        if (message != None):
            if (self.__deviceName != None):
                if (deviceId != None):
                    print(self.__deviceName + " (" + deviceId[:2] + ") " + message)
                else:
                    print(self.__deviceName + " (NOID) " + message)
            else:
                print(message)
                
        
    def changeDeviceId(self,deviceId):
        """
        """
        self.send("CHDEVID"+deviceId)
        self.__deviceId = deviceId[:2]
        message, deviceId = self.waitFor("CHDEVID","--")
        if (message == None):
            raise TimeoutError("Timeout Waiting for CHDEVID")
            
        self.send("DEVNAME")
        message = self.get()[0]
        if (message != None):
            self.__deviceName = message

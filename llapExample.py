# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import time

import llap
import serial

import serialPorts

    
print("The time is " + time.asctime(time.localtime()))

print(serialPorts.listPorts())
    
print("Waiting for device...")

devicePort = 'COM3'
device = []

# Wait until we see that the port path is available
waiting = True
count = 1

while (waiting):
    try:
        # We don't really care about the actual communication
        # rate because we just want to know if the serial
        # path is available. However, we will set the baud
        # rate to 115200 based on the expected spec for our device function.
        # The timeout value applies to any commands we might
        # choose to send in the future.
        device = llap.LLAP(deviceId='--',port=devicePort,baudrate=115200,timeout=1.0,xonxoff=True,rtscts=True,dsrdtr=True)
        device.flush()
        device.start()
        
        waiting = False
        
    except (OSError, serial.SerialException):
        # Don't pass the exception to the caller
        # Display a simple message
        print(str(count) + ") Waiting for " + devicePort + " ...")
        # Wait a short time then keep looping until the exception stops
        time.sleep(1.0)
        count = count + 1
  
try:
    message, deviceId = device.waitFor("STARTED", timeout = 2.0)
    
    if (message == None):
        raise TimeoutError('Timeout Waiting for STARTED')
    device.display(message, deviceId)  
    
    device.changeDeviceId('AA')

    device.send("HELLO")
    message, deviceId = device.waitFor("HELLO")
    if (message == None):
        raise TimeoutError('Timeout Waiting for HELLO')
    device.display(message, deviceId)    
    
    device.send("CYCLE")
    
    startTime = time.time()
    try:
        while ((time.time() - startTime) < 5.0):
            message, deviceId = device.get()
            device.display(message, deviceId)
    except:
        pass
    
    device.send("INTVL500T")
    
    startTime = time.time()
    try:
        while ((time.time() - startTime) < 5.0):
            message, deviceId = device.get()
            device.display(message, deviceId)
    except:
        pass

    device.send("INTVL100T")
    
    startTime = time.time()
    try:
        while ((time.time() - startTime) < 5.0):
            message, deviceId = device.get()
            device.display(message, deviceId)
    except:
        pass

    device.send("INTVL010T")
    
    startTime = time.time()
    try:
        while (True):
            message, deviceId = device.get()
            device.display(message, deviceId)
    except:
        pass

    device.send("STOP")

except (TimeoutError, KeyboardInterrupt) as error:
    print("********************************************")
    print(error)
    print("********************************************")



device.send("STOP")
device.stop()
device.close()


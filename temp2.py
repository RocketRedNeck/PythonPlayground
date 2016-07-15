# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import time
import tkinter as tk

import llap
import serial

# A window interface to use later
win = tk.Tk()
    
print("The time is " + time.asctime(time.localtime()))

    
print("Waiting for arduino...")

arduinoPort = '/dev/tty.usbmodem14331'
arduino = []

# Wait until we see that the port path is available
waiting = True
count = 1

while (waiting):
    try:
        # We don't really care about the actual communication
        # rate because we just want to know if the serial
        # path is available. However, we will set the baud
        # rate to 115200 based on the expected spec for our Arduino function.
        # The timeout value applies to any commands we might
        # choose to send in the future.
        arduino = llap.LLAP(deviceId='--',port=arduinoPort,baudrate=115200,timeout=1.0,xonxoff=True,rtscts=True,dsrdtr=True)
        arduino.flush()
        arduino.start()
        
        waiting = False
        
    except (OSError, serial.SerialException):
        # Don't pass the exception to the caller
        # Display a simple message
        print(str(count) + ") Waiting for " + arduinoPort + " ...")
        # Wait a short time then keep looping until the exception stops
        time.sleep(1.0)
        count = count + 1
  

#sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser),newline='\r\n')

try:
    while (True):
        deviceId, message = arduino.get()
        print("Arduino '" + deviceId + "' said, '" + message + "'")
        if (message == "STARTED--"):
            break
except:
    pass

arduino.send('--','HELLO')
#arduino.write("a--HELLO----\r\n".encode())

deviceId, message = arduino.get()
print("Arduino '" + deviceId + "' said, '" + message + "'")

arduino.write("a--CYCLE----\r\n".encode())

try:
    while (True):
        deviceId, message = arduino.get()
        if (message != '---------'):
            print("Arduino '" + deviceId + "' said, '" + message + "'")
except:
    pass

arduino.write("a--STOP-----\r\n".encode())
arduino.stop()
arduino.close()


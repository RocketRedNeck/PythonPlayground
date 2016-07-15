# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import time
import tkinter as tk

import serial
import io
import serialPorts

# A window interface to use later
win = tk.Tk()
    
ports = serialPorts.listPorts()

print("The time is " + time.asctime(time.localtime()))

print("Looking for serial ports...")
for i in serialPorts.listPorts():
    print(i)
    
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
        arduino = serial.Serial(arduinoPort,115200,timeout=1.0,xonxoff=True,rtscts=True,dsrdtr=True)
        arduino.flush()
        
        waiting = False
        
    except (OSError, serial.SerialException):
        # Don't pass the exception to the caller
        # Display a simple message
        print(str(count) + ") Waiting for " + arduinoPort + " ...")
        # Wait a short time then keep looping until the exception stops
        time.sleep(1.0)
        count = count + 1
  

#sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser),newline='\r\n')

print("Connected!")
time.sleep(1.0)

print("Arduino said, '" + arduino.read(12).decode("utf-8") + "'")

arduino.write("a--HELLO----\r\n".encode())

print("Arduino said, '" + arduino.read(12).decode("utf-8") + "'")

arduino.write("a--CYCLE----\r\n".encode())

while (True):
    print("Arduino said, '" + arduino.read(12).decode("utf-8") + "'")

arduino.close()


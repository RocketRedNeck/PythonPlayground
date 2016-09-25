# -*- coding: utf-8 -*-
"""
Created on Sat May 28 08:53:18 2016

@author: mtkessel
"""

import sys


import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyQt4.QtOpenGL as QtOpenGL

import ctypes
import numpy

import math
from math import pi, sin, cos   # convenience

import time
import llap
import serial

import serialPorts
   

class NavigationThread(QtCore.QThread):
    def __init__(self, navigator, form = None):
        QtCore.QThread.__init__(self)
        self.navigator = navigator
        self.form = form
        self.devicePort = None
        self.device = None
        
        self.on = False
                
    def __del__(self):
        self.wait()

    def setPort(self, port):
        self.devicePort = port
        
    def setOn(self):
        self.on = True
        
    def setOff(self):
        self.on = False

    def displayMessage(self,message,deviceId=None):
        """
        """
        # Only display messages if there is a form to which we can send the messages
        if (self.form != None):
            self.form.displayMessage(message,deviceId)

    def run(self):
        
        # Wait until we see that the port path is available
        waiting = True
        connected = False        
        count = 1
        
        while (waiting and (self.on == True)):
            try:
                # We don't really care about the actual communication
                # rate because we just want to know if the serial
                # path is available. However, we will set the baud
                # rate to 115200 based on the expected spec for our device function.
                # The timeout value applies to any commands we might
                # choose to send in the future.
                self.device = llap.LLAP(deviceId='--',port=self.devicePort,baudrate=115200,timeout=1.0,xonxoff=True,rtscts=True,dsrdtr=True)
                self.device.flush()
                self.device.start()
                
                waiting = False
                
            except (OSError, serial.SerialException):
                # Don't pass the exception to the caller
                # Display a simple message
                if (self.form != None):
                    self.form.displayMessage(str(count) + ": Waiting for " + self.devicePort)
                # Wait a short time then keep looping until the exception stops
                time.sleep(1.0)
                count = count + 1
        
        print("Port Wait Complete")
        if (self.on == True):
            try:
                print("Waiting for STARTED");
                message, deviceId = self.device.waitFor("STARTED", timeout = 2.0, displayAll = True)
                
                if (message == None):
                    self.device.send("ACK")
                    message, deviceId = self.device.waitFor("ACK", timeout = 2.0, displayAll = True)
                
                if (message == None):
                    raise TimeoutError('Timeout Waiting for STARTED')

                self.displayMessage(message, deviceId)  
                
                self.device.changeDeviceId('AA')
            
                self.device.send("HELLO")
                message, deviceId = self.device.waitFor("HELLO")
                if (message == None):
                    raise TimeoutError('Timeout Waiting for HELLO')

                self.displayMessage(message, deviceId)
                
                self.device.send("INTVL010T")
                self.device.send("CYCLE")
                
                connected = True
                
                self.displayMessage("RUNNING")
                                
            except (TimeoutError, KeyboardInterrupt) as error:
                print(str(error))
                connected = False
                if (self.form != None):
                    self.form.displayMessage(str(error))
        
        updateDelta = 1.0/12.0
        nextUpdateTime = time.time() + updateDelta
        
        while (connected and (self.on == True)):
            try:
                message, deviceId = self.device.get(timeout_sec = 0.100)
                if (deviceId == 'PP'):
                    c = message[4:].split(',',13);
                    
                    self.navigator.updateImu(c)
                    

                if (time.time() >= nextUpdateTime):                
                    
                    self.displayMessage(message, deviceId)
                    
                    heading = "{:.1f}".format(self.navigator.heading)
                    roll    = "{:.1f}".format(self.navigator.roll * 180/pi)
                    pitch   = "{:.1f}".format(self.navigator.pitch * 180/pi)
                    yaw     = "{:.1f}".format(self.navigator.yaw * 180/pi)

                    self.displayMessage("HEADING = " + heading + "  (" + roll + ", " + pitch + ", " + yaw + ")")                  
                    
                    nextUpdateTime += updateDelta
                    
            
            except (BaseException) as error:
                print(str(error))
                self.displayMessage(str(error))
        
        print("Connection Loop Exited")
        self.device.send("STOP")
        self.device.stop()
        self.device.close()
        
        if (self.form != None):
            self.form.clearStatus()
        

class Navigator():
    def __init__(self, form = None):
        self.form = form
        self.thread = NavigationThread(self, self.form)        

        # If a form exists, then let the form know
        # which navigoator object is bound to it
        if (self.form != None):
            self.form.bindNavigator(self)
        
#        self.time.gmt = 0
#        
#        self.position.latitude  = 0
#        self.position.longitude = 0
#        
#        self.velocity.magnitude = 0
#
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0
        self.am = 0.0
        
        self.gx = 0.0
        self.gy = 0.0
        self.gz = 0.0
        self.gm = 0.0

        self.mx = 0.0
        self.my = 0.0
        self.mz = 0.0
        self.mm = 0.0
        
        self.LPPsi = 0.0 # for lowpass filter
        
        self.roll  = 0.0    #radians
        self.pitch = 0.0
        self.yaw   = 0.0
        
        self.heading = 0.0  # degrees
                        
    def start(self, port):
        self.thread.setPort(port)
        self.thread.setOn()
        self.thread.start()
        
    def stop(self):
        self.thread.setOff()
        
    def updateImu(self, c):
                
        self.ax = float(c[3])
        self.ay = float(c[4])
        self.az = float(c[5])
        self.am = math.sqrt(self.ax*self.ax + self.ay*self.ay + self.az*self.az)
        
        self.gx = float(c[6])
        self.gy = float(c[7])
        self.gz = float(c[8])
        self.gm = math.sqrt(self.gx*self.gx + self.gy*self.gy + self.gz*self.gz)

        self.mx = float(c[9])
        self.my = float(c[10])
        self.mz = -float(c[11])  # hardware spec indicates mz is opposite of others
        self.mm = math.sqrt(self.mx*self.mx + self.my*self.my + self.mz*self.mz)

        ax = self.ax / self.am        
        ay = self.ay / self.am        
        az = self.az / self.am        

        mx = self.mx / self.mm
        my = self.my / self.mm
        mz = self.mz / self.mm

        phi = math.atan2(ay, az)    # Roll angle
        hyp = math.sqrt(ay*ay + az*az) # hypotenuse
        sphi = ay / hyp # sin of roll angle with correct sign
        cphi = az / hyp # cos of roll angle with correct sign
        
        # rotate magnetic and acceleration components by roll angle (phi)
        bfy = my * cphi - mz * sphi
        bpz = my * sphi + mz * cphi
        gpz = ay * sphi + az * cphi
        
        # compute pitch angle (theta), restricted to +/- 90 degrees
        theta = math.atan2(ax, gpz)
        pi2 = math.pi/2.0
        if (theta > pi2):
            theta = math.pi - theta
            
        if (theta < -pi2):
            theta = -math.pi - theta
        
        # sin and cos of pitch angle
        hyp = math.sqrt(ax*ax + gpz*gpz)
        stheta = - az / hyp
        ctheta = gpz / hyp
        
        # keept pitch in +/- 90 degree range
        if (ctheta < 0):
            ctheta = -ctheta
        
        # rotate by pitch angle (theta)
        bfx = mx * ctheta + bpz * stheta
        bfz = -mx * stheta + bpz * ctheta
        
        # current yaw = e-compass angle
        psi = math.atan2(-bfy, bfx)

# NOTE: This low pass filter is not really working... need to think about it
#        # low pass filter, set up for modulo on 360 degrees
#        temp = psi - self.LPPsi
#        if (temp > math.pi):
#            temp -= 2*math.pi
#            
#        if (temp < -math.pi):
#            temp += 2*math.pi
#        
#        temp = self.LPPsi + temp / 10
#
#        if (temp > math.pi):
#            temp -= 2*math.pi
#            
#        if (temp < -math.pi):
#            temp += 2*math.pi
#
#        self.LPPsi = temp
        
        dtr = math.pi / 180.0
        
        # update pointing information
        self.roll = phi
        self.pitch = theta
        self.yaw = psi
        
        self.heading = -psi / dtr
        
                
           

        
                   
class NavForm(QtGui.QWidget):
   def __init__(self, parent=None):
      super(NavForm, self).__init__(parent)
      
      self.navigator = None
      
      self.resize(500, 750)
      self.move(1400, 300)
      self.setWindowTitle('Navigation Control')
            
      self.onOffButton = QtGui.QPushButton(self)
      
      self.onOffButton.setText("POWER")    
      self.onOffButton.setStyleSheet("color: gray")
    
      self.onOffButton.setCheckable(True)
      self.onOffButton.setDefault(False)
      self.onOffButton.setAutoDefault(False)
      self.onOffButton.setGeometry(400,0,100,50)
      #self.onOffButton.clicked.connect(lambda:self.whichbtn(self.onOffButton))
      self.onOffButton.clicked.connect(self.btnstate)
      
      self.portSelectionBox = QtGui.QComboBox(self)
      s = serialPorts.listPorts()
      self.portSelectionBox.addItems(s)
      
      self.counter = 0;
      self.counterText = QtGui.QLabel(self)
      self.counterText.setGeometry(300,0,100,30)
      self.counterText.setText(str(self.counter))

      self.statusText = [QtGui.QLabel(self),
                         QtGui.QLabel(self),
                         QtGui.QLabel(self),
                         QtGui.QLabel(self),
                         QtGui.QLabel(self),
                         QtGui.QLabel(self),
                         QtGui.QLabel(self)]
      for i in range(len(self.statusText)):
          self.statusText[i].setGeometry(0, 60 + (30*i),500,30)
          self.statusText[i].setText("")
          
      self.statusText[0].setText("OFF")

      			
#   def whichbtn(self,b):
#      print("clicked button is "+b.text())
      
   def clearStatus(self):
      for i in range(len(self.statusText)):
          self.statusText[i].setText("")

      self.statusText[0].setText("OFF")
       
       
   def btnstate(self):
      if self.onOffButton.isChecked():
         self.onOffButton.setDefault(True)
         self.onOffButton.setStyleSheet("color: green")
         if (self.navigator != None):
             self.navigator.start(self.portSelectionBox.currentText())
         self.counter = self.counter + 1
         self.counterText.setText(str(self.counter))
         
      else:
         self.onOffButton.setDefault(False)
         self.onOffButton.setStyleSheet("color: gray")   
         if (self.navigator != None):
             self.navigator.stop()

   def bindNavigator(self, navigator):
        self.navigator = navigator

   def displayMessage(self,message,deviceId=None):
        """
        """
        if (message != None):
            if (deviceId != None):
                if (deviceId == "AA"):
                    self.statusText[1].setText(deviceId[:2] + ": " + message)
                elif (deviceId == "PP"):
                    self.statusText[2].setText(deviceId[:2] + ": " + message)
                elif (deviceId == "GP"):
                    self.statusText[3].setText(deviceId[:2] + ": " + message)
                elif (deviceId == "HH"):
                    self.statusText[4].setText(deviceId[:2] + ": " + message)
                elif (deviceId == "AX"):
                    self.statusText[5].setText(deviceId[:2] + ": " + message)
            else:
                self.statusText[0].setText(message)
                


			
def main():
    
    # We need a navigator to attach to the sensor and accumulate data
    # and we also need form in which to display the data
    app = QtGui.QApplication(sys.argv)      # All Qt applications need this
    app.setStyle('motif')                   # A pleasing non-branded style sheet
    
    # We instantiate a form in which to display data
    # so we can pass it to the navigator; we do it in
    # this order so we can (later) have a navigator that
    # can run without the form (remember the display form
    # is just to the developer/operator visibility into
    # performance of the navigator, but in final applications
    # it won't really be needed or we will want to display
    # things differently)
    navForm = NavForm()
    nav = Navigator(navForm)

    navForm.show()
        
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 08:53:18 2016

@author: mtkessel
"""

import sys

from pyglet.gl import *

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyQt4.QtOpenGL as QtOpenGL

import ctypes
import numpy

import time
import llap
import serial

import serialPorts
   

class NavigationThread(QtCore.QThread):
    def __init__(self, form = None):
        QtCore.QThread.__init__(self)
        self.form = form
        self.devicePort = None
        self.device = None
        
        self.on = False
        
        # temp to test OpenGL updates
        self.x_deg = 0
        self.y_deg = 0
        self.z_deg = 0
        
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
        
        
        if (self.on == True):
            try:
                message, deviceId = self.device.waitFor("STARTED", timeout = 2.0)
                
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
                connected = False
                if (self.form != None):
                    self.form.displayMessage(str(error))
        
        updateDelta = 1.0/24.0
        nextUpdateTime = time.time() + updateDelta
        
        while (connected and (self.on == True)):
            try:
                message, deviceId = self.device.get()

                if (time.time() > nextUpdateTime):                
                    self.displayMessage(message, deviceId)
                    # temporary parsing of the message to compute
                    # an orientation
                    c = message[5:].split(',',9);
                    self.form.quad.xDir = int(c[6])
                    self.form.quad.yDir = int(c[7])
                    self.form.quad.zDir = int(c[8])
                    self.form.quad.updateGL()
                    
                    nextUpdateTime += updateDelta
            
            except:
                pass
            
        self.device.send("STOP")
        self.device.stop()
        self.device.close()
        
        if (self.form != None):
            self.form.clearStatus()
        

class Navigator():
    def __init__(self, form = None):
        self.form = form
        self.thread = NavigationThread(self.form)        

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
#        self.magnetic.x = 1.0
#        self.magnetic.y = 0.0
#        self.magnetic.z = 0.0
#        
#        self.attitude.north = 1.0
#        self.attitude.east  = 0.0
#        self.attitude.down  = 0.0
        
    def start(self, port):
        self.thread.setPort(port)
        self.thread.setOn()
        self.thread.start()
        
    def stop(self):
        self.thread.setOff()
           
class QuadWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setMinimumSize(640/2, 480/2)
        
        # Quad size
        self.height = 0.2
        self.width  = 1
        self.length = 2
        
        self.vx = self.width/2
        self.vy = self.height/4
        self.vz = self.length/2
        
        # Quad 3D start rotation
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0
        
        self.xDir = 1
        self.yDir = 0
        self.zDir = 0
        
    def paintGL(self):
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # NOTES ON COMMENTED OUT CODE
        # Original code was an example of how to get the
        # matrix of a specific look-at by pushing the current
        # stack, resetting the matrix to the identity matrix (1s on diag)
        # and then retriving and inverting the matrix and applying
        # it to the current matrix (matrix multiply)
        # In the end all of that is unecessary for our application
        # because only the look-at is needed (see the code below)
        
        #glPushMatrix()   # store the current MV matrix
        #glLoadIdentity() # clear current MV matrix
        #gluLookAt(0,0,0, self.xDir, self.yDir, self.zDir, 0, -1, 0)
        #mvm = (GLfloat * 16)()
        #glGetFloatv(GL_MODELVIEW_MATRIX, mvm)
        #m = numpy.linalg.inv(numpy.reshape(mvm, [4, 4],'C'))
        #m = numpy.reshape(m, [16], 'C')
        #m = (ctypes.c_float * len(m))(*m.tolist())
        #glPopMatrix();


        # Push Matrix onto stack
        glPushMatrix()
            
        glTranslatef(0.0, 0.0, 0.0)     # Origin where we want the object rotated
        
        # Make the object look-at a specific point from the origin
        # Here we define "up" as "down" (-1) via the screen y-axis
        gluLookAt(0,0,0, self.xDir, self.yDir, self.zDir, 0, -1, 0)

        # See NOTES ON COMMENTED OUT CODE, above                        
        #glMultMatrixf(m)
               
        # NOTE: We don't use glRotatef because it represents a 
        # relative rotation of the current matrix... the code
        # above gives us an absolute orientation
        #glRotatef(self.dxRotation, 1, 0, 0)
        #glRotatef(self.dyRotation, 0, 1, 0)
        #glRotatef(self.dzRotation, 0, 0, 1)
     
        # Draw the positive side of the lines x,y,z
        glBegin(GL_LINES)
        glColor3f (0.0, 1.0, 0.0) # Green for x axis
        glVertex3f(0,0,0)
        glVertex3f(self.vx + 0.5,0,0);
        glColor3f(1.0,0.0,0.0) # Red for y axis
        glVertex3f(0,0,0)
        glVertex3f(0,self.vy + 0.5,0)
        glColor3f(0.0,0.0,1.0) # Blue for z axis
        glVertex3f(0,0,0)
        glVertex3f(0,0,self.vz + 0.5)
        glEnd()
     
        # Draw the six sides of the block
        glBegin(GL_QUADS)
     
        # right/left
        # Magenta
        glColor3ub(255, 0, 255)
        glVertex3f(self.vx, self.vy, self.vz)
        glVertex3f(self.vx, self.vy,-self.vz)
        glVertex3f(self.vx,-self.vy,-self.vz)
        glVertex3f(self.vx,-self.vy, self.vz)
    
        # Blue
        glColor3f(0, 0, 255)
        glVertex3f(-self.vx,-self.vy, self.vz)
        glVertex3f(-self.vx, self.vy, self.vz)
        glVertex3f(-self.vx, self.vy,-self.vz)
        glVertex3f(-self.vx,-self.vy,-self.vz)
     
        # front/back
         # Yellow
        glColor3ub(255, 255, 0)
        glVertex3f( self.vx,  self.vy, self.vz)
        glVertex3f(-self.vx,  self.vy, self.vz)
        glVertex3f(-self.vx, -self.vy, self.vz)
        glVertex3f( self.vx, -self.vy, self.vz)
     
        # Cyan
        glColor3ub( 0, 255, 255)
        glVertex3f(-self.vx,-self.vy,-self.vz)
        glVertex3f( self.vx,-self.vy,-self.vz)
        glVertex3f( self.vx, self.vy,-self.vz)
        glVertex3f(-self.vx, self.vy,-self.vz)
     
        # top/bottom
        # Green
        glColor3ub(0, 255, 0)
        glVertex3f( self.vx, self.vy, self.vz)
        glVertex3f(-self.vx, self.vy, self.vz)
        glVertex3f(-self.vx, self.vy,-self.vz)
        glVertex3f( self.vx, self.vy,-self.vz)
       
        # Red
        glColor3ub(255, 0, 0)
        glVertex3f(-self.vx,-self.vy,-self.vz)
        glVertex3f( self.vx,-self.vy,-self.vz)
        glVertex3f( self.vx,-self.vy, self.vz)
        glVertex3f(-self.vx,-self.vy, self.vz)
       
    
        glEnd()
        
        glFlush()
    
        # Pop Matrix off stack
        glPopMatrix()

    def resizeGL(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(45.0, aspectRatio, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.0) # Back off so we can see the object

    def initializeGL(self):
        glClearColor(0, 0, 0, 1)
        glClearDepth(1.0)              
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()                    
        gluPerspective(45.0,1.33,0.1, 100.0) 
        
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -3.0)    # Back off so we can see the object
        
                   
class NavForm(QtGui.QWidget):
   def __init__(self, parent=None):
      super(NavForm, self).__init__(parent)

      self.navigator = None
      
      self.resize(500, 750)
      self.move(1500, 300)
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
      
      self.quad = QuadWidget(self)
      self.quad.move(75,300)
      			
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

   def updateAttitude(self, dx_deg, dy_deg, dz_deg):
         self.quad.xRotation = dx_deg
         self.quad.yRotation = dy_deg
         self.quad.zRotation = dz_deg
         self.quad.updateGL()

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
    
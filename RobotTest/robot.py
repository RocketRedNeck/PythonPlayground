#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 23:56:25 2018

@author: mtkes
"""

import wpilib
import wpilib.buttons
import wpilib.drive
import wpilib.command

class MyRobot(wpilib.IterativeRobot):

    def robotInit(self):
        self.leftFront = wpilib.Talon(3)
        self.leftRear = wpilib.Talon(1)
        self.rightFront = wpilib.Talon(4)
        self.rightRear = wpilib.Talon(2)
        
        # Create motor groups for WPI-style differential driving
        
        self.leftDrive = wpilib.SpeedControllerGroup(self.leftFront, self.leftRear)
        self.rightDrive = wpilib.SpeedControllerGroup(self.rightFront, self.rightRear)
        
        self.drive = wpilib.drive.DifferentialDrive(self.leftDrive, self.rightDrive)
        
        self.controller = wpilib.Joystick(0)
        
        self.forward  = wpilib.buttons.JoystickButton(self.controller, 4) #TRIANGLE
        self.backward = wpilib.buttons.JoystickButton(self.controller, 2) #CROSS
        self.right    = wpilib.buttons.JoystickButton(self.controller, 3) #CIRCLE
        self.left     = wpilib.buttons.JoystickButton(self.controller, 1) #SQUARE
        
        # Position gets automatically updated as robot moves
        self.gyro = wpilib.AnalogGyro(1)
        
#        self.forward.whenPressed()
#        self.forward.whenReleased()
#        
#        self.backward.whenPressed()
#        self.backward.whenReleased()
#        
#        self.right.whenPressed()
#        self.right.whenReleased()
#        
#        self.left.whenPressed()
#        self.left.whenReleased()
        

    def autonomousInit(self):
        '''Called only at the beginning of autonomous mode'''
        pass

    def autonomousPeriodic(self):
        '''Called every 20ms in autonomous mode'''
        pass

    def disabledInit(self):
        '''Called only at the beginning of disabled mode'''
        pass
    
    def disabledPeriodic(self):
        '''Called every 20ms in disabled mode'''
        pass

    def teleopInit(self):
        '''Called only at the beginning of teleoperated mode'''
        self.leftDrive.set(0)
        self.rightDrive.set(0)
        pass

    def teleopPeriodic(self):
        '''Called every 20ms in teleoperated mode'''
        #wpilib.command.Scheduler.run(self)
        
        # Move a motor with a Joystick
        move = self.controller.getAxis(1)   # LEFT_STICK_Y
        turn = -self.controller.getAxis(2)   # RIGHT_STICK_X

        self.drive.arcadeDrive(move*abs(move), 
                               turn*abs(turn))

if __name__ == '__main__':
    wpilib.run(MyRobot,physics_enabled=True)
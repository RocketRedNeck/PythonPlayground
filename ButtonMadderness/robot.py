#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 23:56:25 2018

@author: mtkes
"""

import wpilib

from wpilib.command import Command
from wpilib.command import Scheduler

from wpilib.joystick import Joystick
from wpilib.buttons import JoystickButton

from subsystems.driveSubsystem import DriveSubsystem
from commands.moveForward import MoveForward
from commands.moveBackward import MoveBackward
from commands.stop import Stop
from commands.turnRight import TurnRight
from commands.turnLeft import TurnLeft

# Put in OI

PS4Axis = {	
   "LEFT_STICK_X"  : 0,
	"LEFT_STICK_Y"  : 1,
	"RIGHT_STICK_X" : 2,
	"L2_AXIS"       : 3,
	"R2_AXIS"       : 4,
	"RIGHT_STICK_Y" : 5
}

	
PS4Button = {    

   "Undefined"    : 0,
	"SQUARE"       : 1, 
	"CROSS"        : 2, 
	"CIRCLE"       : 3, 
	"TRIANGLE"     : 4, 
	"L1"           : 5, 
	"R1"           : 6, 
	"L2"           : 7, 
	"R2"           : 8,
	"SHARE"        : 9, 
	"OPTIONS"      : 10, 
	"L_STICK"      : 11, 
	"R_STICK"      : 12, 
	"PS4"          : 13, 
	"TRACKPAD"     : 14
}

# Do something similar to the above for RobotMap motor IDs and functional
# button mapping
    
class MyRobot(wpilib.IterativeRobot):

    def robotInit(self):
        Command.getRobot = lambda x=0: self
        self.driveSubsystem = DriveSubsystem()
                
        self.controller = Joystick(0)
        
        self.forward  = JoystickButton(self.controller, PS4Button["TRIANGLE"])
        self.backward = JoystickButton(self.controller, PS4Button["CROSS"])
        self.right    = JoystickButton(self.controller, PS4Button["CIRCLE"])
        self.left     = JoystickButton(self.controller, PS4Button["SQUARE"])
                
        self.forward.whileHeld(MoveForward())
        self.forward.whenReleased(Stop())
        
        self.backward.whileHeld(MoveBackward())
        self.backward.whenReleased(Stop())
        
        self.right.whileHeld(TurnRight())
        self.right.whenReleased(Stop())
        
        self.left.whileHeld(TurnLeft())
        self.left.whenReleased(Stop())
                   
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
        pass

    def teleopPeriodic(self):
        '''Called every 20ms in teleoperated mode'''
        Scheduler.getInstance().run()


if __name__ == '__main__':
    wpilib.run(MyRobot,physics_enabled=True)
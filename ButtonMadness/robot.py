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
PS4AxisStrings = [

	"LEFT_STICK_X",
	"LEFT_STICK_Y",
	"RIGHT_STICK_X",
	"L2_AXIS",
	"R2_AXIS",
	"RIGHT_STICK_Y"
]
PS4AxisEnum = enumerate(PS4AxisStrings)
PS4Axis = {}
for i,e in PS4AxisEnum:
    PS4Axis[e] = i 
	
PS4ButtonStrings = [    

   "Undefined",
	"SQUARE", 
	"CROSS", 
	"CIRCLE", 
	"TRIANGLE", 
	"L1", 
	"R1", 
	"L2", 
	"R2",
	"SHARE", 
	"OPTIONS", 
	"L_STICK", 
	"R_STICK", 
	"PS4", 
	"TRACKPAD"
]
PS4ButtonEnum = enumerate(PS4ButtonStrings)
PS4Button = {}
for i,e in PS4ButtonEnum:
    PS4Button[e] = i

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
                
        self.forward.whenPressed(MoveForward())
        self.forward.whenReleased(Stop())
        
        self.backward.whenPressed(MoveBackward())
        self.backward.whenReleased(Stop())
        
        self.right.whenPressed(TurnRight())
        self.right.whenReleased(Stop())
        
        self.left.whenPressed(TurnLeft())
        self.left.whenReleased(Stop())
        
    def disabled(self):
        '''Called when the robot is disabled'''
        pass
            
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
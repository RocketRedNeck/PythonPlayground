import wpilib
from wpilib.command.subsystem import Subsystem

class DriveSubsystem(Subsystem):
    '''
    This example subsystem controls a single Talon in PercentVBus mode.
    '''

    def __init__(self):
        '''Instantiates the motor object.'''

        super().__init__('DriveSubsystem')

        self.leftFront = wpilib.Talon(3)
        self.leftFront.setInverted(True)
        self.leftRear = wpilib.Talon(1)
        self.leftRear.setInverted(True)
        self.rightFront = wpilib.Talon(4)
        self.rightRear = wpilib.Talon(2)

    def stop(self):
    	 self.leftFront.set(0.0);
    	 self.leftRear.set(0.0);
    	 self.rightFront.set(0.0);
    	 self.rightRear.set(0.0);

    def moveForward(self):
    	 self.leftFront.set(0.2);
    	 self.leftRear.set(0.2);
    	 self.rightFront.set(0.2);
    	 self.rightRear.set(0.2);
    
    def moveBackward(self):
    	 self.leftFront.set(-0.2);
    	 self.leftRear.set(-0.2);
    	 self.rightFront.set(-0.2);
    	 self.rightRear.set(-0.2);

    def turnRight(self):
    	 self.leftFront.set(0.2);
    	 self.leftRear.set(0.2);
    	 self.rightFront.set(-0.2);
    	 self.rightRear.set(-0.2);

    def turnLeft(self):
    	 self.leftFront.set(-0.2);
    	 self.leftRear.set(-0.2);
    	 self.rightFront.set(0.2);
    	 self.rightRear.set(0.2);
    

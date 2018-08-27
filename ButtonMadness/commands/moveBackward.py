from wpilib.command import Command

class MoveBackward(Command):
    '''
    This command will read the joystick's y axis and use that value to control
    the speed of the SingleMotor subsystem.
    '''

    def __init__(self):
        super().__init__('Follow Joystick')

        self.requires(self.getRobot().driveSubsystem)


    def execute(self):
        self.getRobot().driveSubsystem.moveBackward()

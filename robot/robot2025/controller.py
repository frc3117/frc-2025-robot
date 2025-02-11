from frctools import Component, RobotBase
from frctools.input import Input

from .climber import Climber
from .conveyor import Conveyor
from .coral_outtake import CoralOuttake
from .elevator import Elevator


class RobotController(Component):
    __climber: Climber = None
    __conveyor: Conveyor = None
    __coral_outtake: CoralOuttake = None
    __elevator: Elevator = None

    __align_input: Input = None
    __intake_input: Input = None
    __outtake_input: Input = None

    def init(self):
        super().__init__()

        self.__climber = self.robot['climber']
        self.__conveyor = self.robot['conveyor']
        self.__coral_outtake = self.robot['coral_outtake']
        self.__elevator = self.robot['elevator']

        self.__align_input = Input.get_input('align')
        self.__intake_input = Input.get_input('intake')
        self.__outtake_input = Input.get_input('outtake')

    def update_teleop(self):
        pass
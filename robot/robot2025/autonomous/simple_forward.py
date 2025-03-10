from frctools import Timer, RobotBase
from frctools.input import Input
from frctools.autonomous import AutonomousSequence


class SimpleForward(AutonomousSequence):
    __vertical_input: Input

    def __init__(self):
        super().__init__()

        self.__vertical_input = Input.get_input('horizontal')

    def loop(self):
        start_time = Timer.get_current_time()

        while Timer.get_elapsed(start_time) < 3:
            self.__vertical_input.override(0.3)
            yield None


from frctools import Component, Timer, CoroutineOrder
from frctools.sensor import Encoder
from frctools.controll import PID
from frctools.frcmath import approximately

import wpiutil


class Elevator(Component):
    def __init__(self, elevator_motor, elevator_encoder: Encoder, controller: PID):
        super().__init__()

        self.__motor = elevator_motor
        self.__encoder = elevator_encoder
        self.__controller = controller

        self.__target_height = 0.

        self.__control_coroutine = None

    def update(self):
        self.__control_coroutine = Timer.start_coroutine_if_stopped(self.__control_loop__, self.__control_coroutine)

    def __control_loop__(self):
        while True:
            error = self.get_current_height() - self.__target_height
            out = self.__controller.evaluate(error)
            self.__motor.set(out)

            yield None

    def set_target_height(self, height: float):
        self.__target_height = height

    def get_current_height(self) -> float:
        return self.__encoder.get()

    def hold_height(self):
        self.set_target_height(self.get_current_height())

    def is_at_target(self, tolerance: float = 0.01) -> bool:
        return approximately(self.__target_height, self.get_current_height(), tolerance)

    def wait_for_height(self, tolerance: float = 0.01):
        yield from ()
        while not self.is_at_target(tolerance):
            yield None

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('height', self.get_current_height, lambda v: None)
        builder.addDoubleProperty('target_height', lambda: self.__target_height, self.set_target_height)

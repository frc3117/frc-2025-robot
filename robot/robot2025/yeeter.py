import math

from frctools import Component, Timer, CoroutineOrder
from frctools.motors import WPI_CANSparkMax
from frctools.sensor import Encoder
from frctools.frcmath import approximately

import wpiutil


BOTTOM_TARGET = 0.4
TOP_TARGET = 0.71


# 8 encoder 15 motor
class Yeeter(Component):
    __motor: WPI_CANSparkMax
    __encoder: Encoder

    __target: float = 0

    __control_coroutine = None

    def __init__(self, motor: WPI_CANSparkMax, encoder: Encoder):
        super().__init__()

        self.__motor = motor
        self.__encoder = encoder

    def init(self):
        self.__target = self.get_angle()

    def update(self):
        self.__control_coroutine = Timer.start_coroutine_if_stopped(self.__control_loop__, self.__control_coroutine, CoroutineOrder.LATE)

    def __control_loop__(self):
        while True:
            if not self.is_at_target(0.02):
                self.__motor.set(math.copysign(0.3, self.error()))
            else:
                self.__motor.set(0)

            yield None

    def get_angle(self) -> float:
        return self.__encoder.get()

    def set_target(self, target: float):
        self.__target = target

    def error(self) -> float:
        return self.get_angle() - self.__target

    def is_at_target(self, tolerance: float = 0.03) -> bool:
        return approximately(self.error(), 0, tolerance)

    def wait_for_target(self, tolerance: float = 0.03):
        yield from ()
        while not self.is_at_target(tolerance):
            yield None

    def yeet(self):
        self.set_target(BOTTOM_TARGET)
        yield from self.wait_for_target(0.03)

        self.set_target(TOP_TARGET)
        yield from self.wait_for_target(0.03)

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('angle', self.get_angle, lambda v: None)
        builder.addDoubleProperty('error', self.error, lambda v: None)
        builder.addBooleanProperty('at_target', self.is_at_target, lambda v: None)

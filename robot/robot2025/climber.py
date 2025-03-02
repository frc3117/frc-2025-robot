from frctools import Component, Timer, WPI_CANSparkMax
from frctools.sensor import Encoder
from frctools.frcmath import approximately
from math import copysign

import wpiutil


class Climber(Component):
    __angle_motor = WPI_CANSparkMax
    __angle_encoder: Encoder

    __target_angle: float

    __control_coroutine = None


    def __init__(self, angle_motor:WPI_CANSparkMax, angle_encoder: Encoder):
        super().__init__()

        self.__angle_motor = angle_motor
        self.__angle_encoder = angle_encoder

        self.__target_angle = self.__angle_encoder.get()

    def update(self):
        self.__control_coroutine = Timer.start_coroutine_if_stopped(self.__control_loop__, self.__control_coroutine)

    def __control_loop__(self):
        while True:
            if not(self.is_at_angle()):
                error_angle = self.__target_angle - self.get_current_angle()
                self.__angle_motor.set(copysign(0.2, error_angle))
            else:
                self.__angle_motor.set(0)
            yield None

    def set_target_angle(self, angle:float):
        self.__target_angle = angle

    def get_current_angle(self) -> float:
        return self.__angle_encoder.get()

    def hold_angle(self):
        self.set_target_angle(self.get_current_angle())

    def is_at_angle(self, tolerance: float = 0.01) -> bool:
        return approximately(self.__target_angle, self.get_current_angle(), tolerance)

    def wait_for_angle(self, tolerance: float = 0.01):
        yield from ()
        while not self.is_at_angle(tolerance):
            yield None

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('angle', self.get_current_angle, lambda v: None)
        builder.addDoubleProperty('target_height', lambda: self.__target_angle, self.set_target_angle)

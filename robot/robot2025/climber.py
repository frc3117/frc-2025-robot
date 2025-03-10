from frctools import Component, Timer
from frctools.motors import WPI_CANSparkMax
from frctools.sensor import Encoder
from frctools.frcmath import approximately, clamp
from math import copysign

import wpiutil


class Climber(Component):
    __angle_motor = None
    __angle_encoder: Encoder

    __speed: float = 0.

    __control_coroutine = None

    def __init__(self, angle_motor: WPI_CANSparkMax, angle_encoder: Encoder):
        super().__init__()

        self.__angle_motor = angle_motor
        self.__angle_encoder = angle_encoder

    def init(self):
        super().init()

        self.__speed = 0.

    def update(self):
        self.__control_coroutine = Timer.start_coroutine_if_stopped(self.__control_loop__, self.__control_coroutine)

    def __control_loop__(self):
        while True:
            min_s = -1.
            max_s = 1.

            if self.get_current_angle() >= 0.30:
                max_s = 0
            elif self.get_current_angle() <= 0.03:
                min_s = 0

            self.__angle_motor.set(clamp(self.__speed, min_s, max_s))
            yield None

    def get_current_angle(self) -> float:
        return self.__angle_encoder.get()

    def set_speed(self, speed: float):
        self.__speed = speed

    def get_speed(self):
        return self.__speed

    #def set_up(self):
    #    self.set_target_angle(0.273)

    #def is_at_angle(self, tolerance: float = 0.02) -> bool:
    #    return approximately(self.__target_angle, self.get_current_angle(), tolerance)

    def wait_for_angle(self, target, tolerance: float = 0.03):
        yield from ()
        while not approximately(target, self.get_current_angle(), tolerance):
            error_angle = target - self.get_current_angle()
            self.set_speed(copysign(0.3, error_angle))
            yield None

        self.set_speed(0)

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('angle', self.get_current_angle, lambda v: None)
        builder.addDoubleProperty('speed', self.get_speed, lambda v: None)

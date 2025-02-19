from frctools import Component, Timer
from frctools.sensor import Encoder
from frctools.frcmath import approximately
from math import copysign


class Climber(Component):
    __angle_motor = None
    __claw_motor = None
    __angle_encoder: Encoder
    __claw_encoder: Encoder

    __target_angle: float
    __target_angle_claw: float

    __control_coroutine = None


    def __init__(self):
        super().__init__()

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


    def set_target_claw_angle(self, claw_angle: float):
        self.__target_angle_claw = claw_angle

    def get_current_claw_angle(self):
        return self.__claw_encoder.get()

    def hold_claw_angle(self):
        self.set_target_claw_angle(self.get_current_claw_angle())

    def is_at_claw_angle(self, tolerance: float = 0.01) -> bool:
        return approximately(self.__target_angle_claw, self.get_current_claw_angle(), tolerance)

    def wait_for_angle(self, tolerance: float = 0.01):
        yield from ()
        while not self.is_at_claw_angle(tolerance):
            yield None

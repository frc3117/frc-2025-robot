import math

from frctools import Component, Timer, CoroutineOrder, WPI_CANSparkFlex
from frctools.sensor import Encoder
from frctools.controll import PID, LeakyIntegrator
from frctools.frcmath import approximately, clamp

from wpilib import DigitalInput, SmartDashboard

import wpiutil

FEEDING_HEIGHT = 0.042
STAGES_HEIGHT = [
    0.221,
    0.221,
    0.493,
    0.95,
]


class Elevator(Component):
    __motor: WPI_CANSparkFlex = None
    __encoder: Encoder = None
    __controller: PID = None
    __top_limit_switch: DigitalInput = None
    __bottom_limit_switch: DigitalInput = None

    __target_height: float = 0.
    __target_height_smooth: float = 0.
    __target_leaky: LeakyIntegrator = LeakyIntegrator()
    __error_leaky: LeakyIntegrator = LeakyIntegrator()
    __error_moving_average: float = 0.

    __control_coroutine = None

    __first_run = False

    def __init__(self,
                 elevator_motor,
                 elevator_encoder: Encoder,
                 controller: PID,
                 top_limit_switch: DigitalInput = None,
                 bottom_limit_switch: DigitalInput = None):
        super().__init__()

        self.__motor = elevator_motor
        self.__encoder = elevator_encoder
        self.__controller = controller
        self.__top_limit_switch = top_limit_switch
        self.__bottom_limit_switch = bottom_limit_switch

        self.__control_coroutine = None

        SmartDashboard.putData('Elevator/pid', self.__controller)

        self.__target_lambda = 0.9
        self.__error_lambda = 0.85

    def init(self):
        if not self.__first_run:
            self.__target_height = self.get_current_height()
            self.__target_leaky.current = self.__target_height
            self.__first_run = True

        self.__error_leaky.current = abs(self.true_error())

    def update(self):
        self.__target_leaky.evaluate(self.__target_height, self.__target_lambda)
        self.__error_leaky.evaluate(abs(self.true_error()), self.__error_lambda)

        self.__control_coroutine = Timer.start_coroutine_if_stopped(self.__control_loop__, self.__control_coroutine, CoroutineOrder.LATE)

    def __control_loop__(self):
        while True:
            if not self.is_at_target():
                error = self.error()
                error_sign = math.copysign(1, error)
                if error_sign == 1:
                    ff = 1
                else:
                    ff = -0.5

                out = self.__controller.evaluate(error, ff)

                min_val = -1
                max_val = 1
                if self.get_top_limit():
                    max_val = 0
                if self.get_bottom_limit():
                    min_val = 0

                self.__motor.set(clamp(out, min_val, max_val))
            else:
                self.__controller.reset_integral()
                self.__motor.set(0)

            yield None

    def set_motor(self, value):
        min_val = -1
        max_val = 1
        if self.get_top_limit():
            max_val = 0
        if self.get_bottom_limit():
            min_val = 0

        self.__motor.set(clamp(value, min_val, max_val))

    def set_feeding_height(self):
        self.set_target_height(FEEDING_HEIGHT)

    def set_stage(self, stage: int):
        self.set_target_height(STAGES_HEIGHT[stage])

    def set_target_height(self, height: float):
        self.__target_height = height
        self.__error_leaky.current = self.error()

    def get_current_height(self) -> float:
        return self.__encoder.get()

    def hold_height(self):
        self.set_target_height(self.get_current_height())

    def is_at_target(self, tolerance: float = 0.0025) -> bool:
        return approximately(self.__error_leaky.current, 0, tolerance)

    def wait_for_height(self, tolerance: float = 0.0025):
        yield from ()
        while not self.is_at_target(tolerance):
            yield None

    def error(self) -> float:
        return self.__target_leaky.current - self.get_current_height()

    def true_error(self) -> float:
        return self.__target_height - self.get_current_height()

    def get_top_limit(self) -> bool:
        return self.__top_limit_switch is not None and self.__top_limit_switch.get()

    def get_bottom_limit(self) -> bool:
        return self.__bottom_limit_switch is not None and self.__bottom_limit_switch.get()

    def __set_target_lambda__(self, l: float):
        self.__target_lambda = l

    def __set_error_lambda__(self, l: float):
        self.__error_lambda = l

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('height', self.get_current_height, lambda v: None)
        builder.addDoubleProperty('height_raw', self.__encoder.get_raw, lambda v: None)
        builder.addDoubleProperty('target_height', lambda: self.__target_height, self.set_target_height)
        builder.addDoubleProperty('error', self.error, lambda v: None)
        builder.addDoubleProperty('true_error', self.true_error, lambda v: None)
        builder.addDoubleProperty('smooth_error', lambda: self.__error_leaky.current, lambda v: None)
        builder.addBooleanProperty('top_limit', self.get_top_limit, lambda v: None)
        builder.addBooleanProperty('bottom_limit', self.get_bottom_limit, lambda v: None)
        builder.addBooleanProperty('at_height', self.is_at_target, lambda v: None)

        builder.addDoubleProperty('target_lambda', lambda: self.__target_lambda, self.__set_target_lambda__)
        builder.addDoubleProperty('error_lambda', lambda: self.__error_lambda, self.__set_error_lambda__)

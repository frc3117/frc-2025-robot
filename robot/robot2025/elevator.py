import math

from frctools import Component, Timer, CoroutineOrder, WPI_CANSparkFlex
from frctools.sensor import Encoder
from frctools.controll import PID
from frctools.frcmath import approximately, clamp

from wpilib import DigitalInput, SmartDashboard

import wpiutil

FEEDING_HEIGHT = 0.0514
STAGES_HEIGHT = [
    0.23,
    0.23,
    0.518,
    0.958,
]


class Elevator(Component):
    __motor: WPI_CANSparkFlex = None
    __encoder: Encoder = None
    __controller: PID = None
    __top_limit_switch: DigitalInput = None
    __bottom_limit_switch: DigitalInput = None

    __target_height: float = 0.
    __target_height_smooth: float = 0.
    __error_moving_average: float = 0.

    __control_coroutine = None

    def __init__(self,
                 elevator_motor,
                 elevator_encoder: Encoder,
                 controller: PID,
                 top_limit_switch: DigitalInput,
                 bottom_limit_switch: DigitalInput):
        super().__init__()

        self.__motor = elevator_motor
        self.__encoder = elevator_encoder
        self.__controller = controller
        self.__top_limit_switch = top_limit_switch
        self.__bottom_limit_switch = bottom_limit_switch

        self.__target_height = self.get_current_height()
        self.__target_height_smooth = self.__target_height

        self.__control_coroutine = None

        SmartDashboard.putData('Elevator/pid', self.__controller)

        self.__target_gain = 0.9

    def init(self):
        self.__error_moving_average = self.error()

    def update(self):
        self.__evaluate_target__(self.__target_gain)
        self.__evaluate_error__(0.85)
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
                if self.__top_limit_switch.get():
                    max_val = 0
                if self.__bottom_limit_switch.get():
                    min_val = 0

                self.__motor.set(clamp(out, min_val, max_val))
            else:
                self.__controller.reset_integral()
                self.__motor.set(0)

            yield None

    def set_motor(self, value):
        min_val = -1
        max_val = 1
        if self.__top_limit_switch.get():
            max_val = 0
        if self.__bottom_limit_switch.get():
            min_val = 0

        self.__motor.set(clamp(value, min_val, max_val))

    def set_feeding_height(self):
        self.set_target_height(FEEDING_HEIGHT)

    def set_stage(self, stage: int):
        self.set_target_height(STAGES_HEIGHT[stage])

    def set_target_height(self, height: float):
        self.__target_height = height
        self.__error_moving_average = self.error()

    def get_current_height(self) -> float:
        return self.__encoder.get()

    def hold_height(self):
        self.set_target_height(self.get_current_height())

    def is_at_target(self, tolerance: float = 0.0025) -> bool:
        return approximately(self.__error_moving_average, 0, tolerance)

    def wait_for_height(self, tolerance: float = 0.0025):
        yield from ()
        while not self.is_at_target(tolerance):
            yield None

    def error(self) -> float:
        return self.__target_height_smooth - self.get_current_height()

    def true_error(self) -> float:
        return self.__target_height - self.get_current_height()

    def __evaluate_target__(self, gain: float = 0.85):
        self.__target_height_smooth = gain * self.__target_height_smooth + (1 - gain) * self.__target_height

    def __evaluate_error__(self, gain: float = 0.85):
        self.__error_moving_average = gain * self.__error_moving_average + (1 - gain) * abs(self.true_error())

    def __set_target_gain__(self, gain: float):
        self.__target_gain = gain

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addDoubleProperty('height', self.get_current_height, lambda v: None)
        builder.addDoubleProperty('height_raw', self.__encoder.get_raw, lambda v: None)
        builder.addDoubleProperty('target_height', lambda: self.__target_height, self.set_target_height)
        builder.addDoubleProperty('error', self.error, lambda v: None)
        builder.addDoubleProperty('true_error', self.true_error, lambda v: None)
        builder.addDoubleProperty('smooth_error', lambda: self.__error_moving_average, lambda v: None)
        builder.addBooleanProperty('top_limit', self.__top_limit_switch.get, lambda v: None)
        builder.addBooleanProperty('bottom_limit', self.__bottom_limit_switch.get, lambda v: None)
        builder.addBooleanProperty('at_height', self.is_at_target, lambda v: None)

        builder.addDoubleProperty('target_gain', lambda: self.__target_gain, self.__set_target_gain__)

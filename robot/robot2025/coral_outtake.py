from frctools import Component, WPI_CANSparkMax, Timer

from wpilib import DigitalInput

import wpiutil


class CoralOuttake(Component):
    __motor: WPI_CANSparkMax
    __prox: DigitalInput

    def __init__(self, motor: WPI_CANSparkMax, prox: DigitalInput):
        super().__init__()

        self.__motor = motor
        self.__prox = prox

    def has_coral(self):
        return not self.__prox.get()

    def feed_coral(self):
        yield from ()
        while not self.has_coral():
            self.__motor.set(0.2)
            yield

        while self.has_coral():
            self.__motor.set(0.2)
            yield

        self.__motor.set(0)

    def shoot_coral(self):
        yield from ()

        start_time = Timer.get_current_time()
        while Timer.get_elapsed(start_time) < 0.6:
            self.__motor.set(0.6)
            yield

        self.__motor.set(0)

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addBooleanProperty('has_coral', self.has_coral, lambda v: None)

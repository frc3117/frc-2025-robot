from frctools import Component, WPI_CANSparkMax

from wpilib import DigitalInput

import wpiutil


class Conveyor(Component):
    __motor: WPI_CANSparkMax
    __prox: DigitalInput

    def __init__(self, motor: WPI_CANSparkMax, prox: DigitalInput):
        super().__init__()

        self.__motor = motor
        self.__prox = prox

    def has_coral(self):
        return self.__prox.get()

    def wait_for_coral(self):
        yield from ()
        while not self.has_coral():
            yield None

    def send_coral(self):
        yield from ()
        while self.has_coral():
            self.__motor.set(0.2)
            yield None

        self.__motor.set(0)

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addBooleanProperty('has_coral', self.has_coral, lambda v: None)

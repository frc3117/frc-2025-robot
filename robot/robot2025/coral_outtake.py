from frctools import Component, WPI_CANSparkMax

from wpilib import DigitalInput

import wpiutil


class CoralOuttake(Component):
    __motor: WPI_CANSparkMax
    __prox: DigitalInput

    def __init__(self):
        super().__init__()

    def has_coral(self):
        return self.__prox.get()

    def feed_coral(self):
        yield from ()
        while not self.has_coral():
            self.__motor.set(0.2)

        self.__motor.set(0)

    def shoot_coral(self):
        yield from ()
        while self.has_coral():
            self.__motor.set(0.4)

        self.__motor.set(0)

    def initSendable(self, builder: wpiutil.SendableBuilder):
        builder.addBooleanProperty('has_coral', self.has_coral, lambda v: None)

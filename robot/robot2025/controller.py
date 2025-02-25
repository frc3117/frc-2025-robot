from frctools import Component, Timer, CoroutineOrder
from frctools.input import Input

from .climber import Climber
from .conveyor import Conveyor
from .coral_outtake import CoralOuttake
from .elevator import Elevator


class RobotController(Component):
    __climber: Climber = None
    __conveyor: Conveyor = None
    __coral_outtake: CoralOuttake = None
    __elevator: Elevator = None

    __align_input: Input = None
    __intake_input: Input = None
    __outtake_input: Input = None

    __manual_elevator_up_input = None
    __manual_elevator_down_input = None

    __logic_coroutine = None

    def init(self):
        super().__init__()

        #self.__climber = self.robot['Climber']
        self.__conveyor = self.robot['Conveyor']
        self.__coral_outtake = self.robot['CoralOuttake']
        self.__elevator = self.robot['Elevator']

        self.__align_input = Input.get_input('align')
        self.__intake_input = Input.get_input('intake')
        self.__outtake_input = Input.get_input('outtake')

        self.__manual_elevator_up_input = Input.get_input('manual_elevator_up')
        self.__manual_elevator_down_input = Input.get_input('manual_elevator_down')

    def update_teleop(self):
        self.__logic_coroutine = Timer.start_coroutine_if_stopped(self.__logic_loop__, self.__logic_coroutine, CoroutineOrder.EARLY)

    def __logic_loop__(self):
        i = 0
        while True:
            self.__elevator.set_feeding_height()
            yield from self.__intake_input.wait_until('up')

            # Feed Coral
            while not self.__conveyor.has_coral():
                self.__conveyor.feed_coral(0.7)

                yield None

            self.__conveyor.feed_coral(0)

            yield from self.__elevator.wait_for_height()
            yield from Timer.wait_parallel(
                self.__conveyor.send_coral(),
                self.__coral_outtake.feed_coral()
            )

            self.__elevator.set_stage(2 + (i % 2))
            i += 1

            yield from self.__elevator.wait_for_height()

            yield from self.__outtake_input.wait_until('up')
            yield from self.__coral_outtake.shoot_coral()
            yield from self.__outtake_input.wait_until('up')

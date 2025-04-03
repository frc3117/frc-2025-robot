from frctools import RobotBase, Timer
from frctools.autonomous import AutonomousSequence
from frctools.input import Input
from frctools.vision.apriltags import AprilTagsReefscapeField

from .. import RobotController
from ..driver_station import ReefSelector


class NoTagException(Exception):
    pass


class MultiCoral(AutonomousSequence):
    __controller: RobotController

    __is_left: bool

    __align_input: Input = None
    __intake_input: Input = None
    __outtake_input: Input = None
    __vertical_input: Input = None
    __horizontal_input: Input = None
    __rotation_input: Input = None

    def __init__(self, is_left: bool):
        super().__init__()

        self.__controller = RobotBase.instance().get_component('RobotController')

        self.__is_left = is_left

        self.__align_input = Input.get_input('align')
        self.__intake_input = Input.get_input('intake')
        self.__outtake_input = Input.get_input('outtake')
        self.__vertical_input = Input.get_input('horizontal')
        self.__horizontal_input = Input.get_input('vertical')
        self.__rotation_input = Input.get_input('rotation')

    def align_on_tag(self, tag, position, cam_id: int, feeding: bool = False):
        yield from ()

        if not tag.is_detected:
            raise NoTagException()

        self.__controller.custom_align(tag, cam_id, position)

        aligned_event = self.__controller.robot_aligned_block()
        if feeding:
            bypass_event = self.__controller.coral_in_intake_block()
        else:
            bypass_event = None

        while not aligned_event.is_ready():
            if bypass_event is not None and bypass_event.is_ready():
                break

            self.__align_input.override(True)
            yield None

    def deliver_coral(self, tag, height: int, is_left: bool):
        yield from ()

        ReefSelector.set_value(height + (0 if is_left else 4))

        # Make the elevator go to the target height
        self.__intake_input.override(True)
        yield from self.__controller.elevator_at_height_block()

        if not tag.is_detected:
            raise NoTagException()

        self.__controller.custom_align(tag, 0, self.__controller.get_reef_target(is_left))

        aligned_event = self.__controller.robot_aligned_block()
        elevator_height_event = self.__controller.elevator_at_height_block()
        while not aligned_event.is_ready():
            self.__align_input.override(True)
            yield None

        # Also wait in case elevator is not at height yet
        yield from elevator_height_event

        # Shoot the coral
        self.__outtake_input.override(True)
        yield from self.__controller.wait_for_coral_shot()
        self.__intake_input.override(True)
    
    def feed_coral(self, tag):
        yield from ()

        coral_in_intake = self.__controller.coral_in_intake_block()
        coral_in_elevator = self.__controller.coral_in_elevator_block()

        # Feed Coral
        self.__intake_input.override(True)

        if tag is not None:
            yield from self.align_on_tag(tag, self.__controller.get_coral_station_target(), 1, feeding=True)

        # Wait for coral to be fed and become into the elevator
        yield from coral_in_intake
        yield from coral_in_elevator

    def move_to_toward_station(self, tag):
        yield from ()

        ratio = 1 if self.__is_left else -1

        start_time = Timer.get_current_time()
        while Timer.get_elapsed(start_time) <= 3:
            self.__horizontal_input.override(0.2 * ratio)
            self.__vertical_input.override(0.2)

            self.__rotation_input.override(-0.06 * ratio)

            if tag.is_detected:
                break

            yield None

        while not tag.is_detected:
            yield None

    def loop(self):
        reef = AprilTagsReefscapeField.get_reef()
        coral_stations = AprilTagsReefscapeField.get_coral_station()

        if self.__is_left:
            first_tag = reef.f
            first_is_left = False
            station_tag = coral_stations.left
            reef_tag = reef.e
        else:
            first_tag = reef.b
            first_is_left = True
            station_tag = coral_stations.right
            reef_tag = reef.c

        try:
            yield from self.feed_coral(None)
            yield from self.deliver_coral(first_tag, 3, first_is_left)
        except NoTagException:
            print('No tags detected')
            start_time = Timer.get_current_time()
            while Timer.get_elapsed(start_time) < 1.5:
                self.__vertical_input.override(0.3)
                yield None
            return
        except Exception as e:
            print(e)
            return

        try:
            yield from self.move_to_toward_station(station_tag)

            yield from self.feed_coral(station_tag)
            yield from self.deliver_coral(reef_tag, 3, False)

            yield from self.feed_coral(station_tag)
            yield from self.deliver_coral(reef_tag, 3, True)
        except NoTagException:
            print('No more tag detected')
        except Exception as e:
            print(e)
            pass

    def on_end(self):
        self.__controller.clear_custom_align()
        
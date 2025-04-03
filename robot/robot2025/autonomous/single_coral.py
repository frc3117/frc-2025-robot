from frctools import RobotBase, Timer
from frctools.input import Input
from frctools.autonomous import AutonomousSequence
from frctools.vision.apriltags import AprilTagsReefscapeField

from .. import RobotController


class SingleCoral(AutonomousSequence):
    __controller: RobotController

    __align_input: Input = None
    __intake_input: Input = None
    __outtake_input: Input = None
    __vertical_input: Input = None

    def __init__(self):
        super().__init__()

        self.__controller = RobotBase.instance().get_component('RobotController')

        self.__align_input = Input.get_input('align')
        self.__intake_input = Input.get_input('intake')
        self.__outtake_input = Input.get_input('outtake')
        self.__vertical_input = Input.get_input('horizontal')

    def loop(self):
        # Feed Coral
        self.__intake_input.override(True)

        # Wait for coral to be fed and become into the elevator
        yield from self.__controller.wait_for_coral_in_intake()
        yield from self.__controller.wait_for_coral_in_elevator()

        # Make the elevator go to the target height
        self.__intake_input.override(True)
        yield from self.__controller.elevator_at_height_block()

        tag = AprilTagsReefscapeField.get_reef().f
        if not tag.is_detected:
            print('Not detected :(')
            return

        self.__controller.custom_align(tag, 0, self.__controller.get_reef_target(False))

        #if len(AprilTagsReefscapeField.get_reef().detected) <= 0:
        #    for t in AprilTagsReefscapeField.get_reef().all:
        #        print(f'{t.id}:{t.is_detected}')
        #
            #print('No tags detected')
            #start_time = Timer.get_current_time()
            #while Timer.get_elapsed(start_time) < 3:
            #    self.__vertical_input.override(0.3)
            #    yield None
        #
        #    return

        # Align the robot to the reef
        aligned_event = self.__controller.robot_aligned_block()
        elevator_height_event = self.__controller.elevator_at_height_block()
        while not aligned_event.is_ready():
            self.__align_input.override(True)
            yield None

        # Also wait in case elevator is not at height yet
        yield from elevator_height_event

        # Shoot the coral
        self.__outtake_input.override(True)

    def on_end(self):
        self.__controller.clear_custom_align()

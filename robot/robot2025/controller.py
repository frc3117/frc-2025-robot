import math

from frctools import Component, Timer, CoroutineOrder, LED, ConcurrentEvent
from frctools.input import Input
from frctools.drivetrain import SwerveDrive
from frctools.frcmath import clamp, delta_angle, approximately, Vector2
from frctools.vision.apriltags import AprilTagsReefscapeField, AprilTagsFieldPose

from .climber import Climber
from .conveyor import Conveyor
from .coral_outtake import CoralOuttake
from .elevator import Elevator
from .driver_station import ReefSelector

from enum import Enum
from typing import List


CORAL_STATION_TARGET = Vector2(0, 0.545)
REEF_LEFT_TARGET = Vector2(0.224, 0.459)
REEF_RIGHT_TARGET = Vector2(-0.123, 0.459)

TARGET_ANGLES = {}


def add_angle_pair(value: float, keys):
    TARGET_ANGLES[keys[0]] = value
    TARGET_ANGLES[keys[1]] = value

# ID 10 and 21
REFERENCE = 0

# Reef
add_angle_pair(REFERENCE, (10, 21))
add_angle_pair(REFERENCE + 5.236, (9, 22))
add_angle_pair(REFERENCE + 4.189, (8, 17))
add_angle_pair(REFERENCE + math.pi, (7, 18))
add_angle_pair(REFERENCE + 2.094, (6, 19))
add_angle_pair(REFERENCE + 1.047, (11, 20))

# Coral Station
add_angle_pair(REFERENCE + 2.182, (1, 13))
add_angle_pair(REFERENCE + 4.102, (2, 12))


def tags_from_cam(tags: List[AprilTagsFieldPose], cam_id: int):
    return [t for t in tags if t.nt.get_cam_id() == cam_id and t.is_detected]


def power_transform(val, exp):
    return math.copysign(math.pow(min(abs(val), 1), exp), val)


class AlignTarget(int, Enum):
    NONE = -1
    CORAL_STATION = 0
    REEF = 1
    CUSTOM = 2


class RobotController(Component):
    __swerve: SwerveDrive = None
    __climber: Climber = None
    __conveyor: Conveyor = None
    __coral_outtake: CoralOuttake = None
    __elevator: Elevator = None
    __led: LED = None

    __align_input: Input = None
    __intake_input: Input = None
    __outtake_input: Input = None
    __climb_input: Input = None
    __recalibrate_input: Input = None

    __manual_climber_up_input = None
    __manual_climber_down_input = None

    __horizontal_input: Input = None
    __vertical_input: Input = None
    __rotation_input: Input = None

    __align_target: AlignTarget = None

    __coral_logic_loop = None
    __align_logic_loop = None
    __climb_logic_loop = None
    __recalibrate_logic_loop = None

    __should_align: bool = False
    __target_position = None
    __target_angle = None
    __target_error = 0.

    __align_tag: AprilTagsFieldPose = None
    __align_cam_id = -1
    __align_position: Vector2 = None

    __swerve_speed = 1.

    __ready_to_feed_event: ConcurrentEvent
    __coral_in_intake_event: ConcurrentEvent
    __coral_in_elevator_event: ConcurrentEvent
    __elevator_at_height_event: ConcurrentEvent
    __coral_shot_event: ConcurrentEvent
    __robot_aligned_event: ConcurrentEvent

    def __init__(self):
        super().__init__()

        self.__ready_to_feed_event = ConcurrentEvent()
        self.__coral_in_intake_event = ConcurrentEvent()
        self.__coral_in_elevator_event = ConcurrentEvent()
        self.__elevator_at_height_event = ConcurrentEvent()
        self.__coral_shot_event = ConcurrentEvent()
        self.__robot_aligned = ConcurrentEvent()

    def init(self):
        super().__init__()

        self.__swerve = self.robot['Swerve']
        self.__climber = self.robot['Climber']
        self.__conveyor = self.robot['Conveyor']
        self.__coral_outtake = self.robot['CoralOuttake']
        self.__elevator = self.robot['Elevator']
        self.__led = self.robot['LED']

        self.__align_input = Input.get_input('align')
        self.__intake_input = Input.get_input('intake')
        self.__outtake_input = Input.get_input('outtake')
        self.__climb_input = Input.get_input('climb')
        self.__recalibrate_input = Input.get_input('recalibrate')

        self.__manual_climber_up_input = Input.get_input('manual_climber_up')
        self.__manual_climber_down_input = Input.get_input('manual_climber_down')

        self.__horizontal_input = Input.get_input('horizontal')
        self.__vertical_input = Input.get_input('vertical')
        self.__rotation_input = Input.get_input('rotation')

        self.reef_align()
        #self.custom_align(AprilTagsReefscapeField.get_reef().c, 0, REEF_LEFT_TARGET)

    def update_disabled(self):
        self.__led.set_color((255, 0, 0), 1)

    def update_auto(self):
        self.__led.set_color((255, 255, 0), 2)

    def update(self):
        self.__coral_logic_loop = Timer.start_coroutine_if_stopped(self.__coral_logic_loop__, self.__coral_logic_loop, CoroutineOrder.EARLY, ignore_stop_all=True)
        self.__align_logic_loop = Timer.start_coroutine_if_stopped(self.__align_logic_loop__, self.__align_logic_loop, CoroutineOrder.EARLY, ignore_stop_all=True)
        self.__climb_logic_loop = Timer.start_coroutine_if_stopped(self.__climb_logic_loop__, self.__climb_logic_loop, CoroutineOrder.EARLY)
        self.__recalibrate_logic_loop = Timer.start_coroutine_if_stopped(self.__recalibrate_logic_loop__, self.__recalibrate_logic_loop, CoroutineOrder.EARLY, ignore_stop_all=True)

        self.__led.set_color((0, 255, 0), 2)

        self.__swerve_speed = clamp(-0.8 * self.__elevator.get_current_height() + 1.2, 0., 1.)
        self.__swerve.set_speed(self.__swerve_speed)

        self.__should_align = self.__align_input.get()

    def none_align(self):
        self.__align_target = AlignTarget.NONE

    def coral_station_align(self):
        self.__align_target = AlignTarget.CORAL_STATION

    def reef_align(self):
        self.__align_target = AlignTarget.REEF

    def custom_align(self, tag: AprilTagsFieldPose, cam_id: int, position: Vector2):
        self.__align_tag = tag
        self.__align_cam_id = cam_id
        self.__align_position = position

    def wait_for_ready_to_feed(self):
        yield from self.__ready_to_feed_event.create_block()

    def ready_to_feed_block(self):
        return self.ready_to_feed_block()

    def wait_for_coral_in_intake(self):
        yield from self.__coral_in_intake_event.create_block()

    def coral_in_intake_block(self):
        return self.__coral_in_intake_event.create_block()

    def wait_for_coral_in_elevator(self):
        yield from self.__coral_in_elevator_event.create_block()

    def coral_in_elevator_block(self):
        return self.__coral_in_elevator_event

    def wait_for_elevator_at_height(self):
        yield from self.__elevator_at_height_event.create_block()

    def elevator_at_height_block(self):
        return self.__elevator_at_height_event.create_block()

    def wait_for_coral_shot(self):
        yield from self.__coral_shot_event.create_block()

    def coral_shot_block(self):
        return self.__coral_shot_event.create_block()

    def wait_robot_aligned(self):
        yield from self.__robot_aligned_event.create_block()

    def robot_aligned_block(self):
        return self.__robot_aligned_event.create_block()

    def __coral_logic_loop__(self):
        while True:
            self.coral_station_align()
            self.__elevator.set_feeding_height()

            self.__ready_to_feed_event.set()

            # Feed Coral
            feed_coral = False
            while not self.__conveyor.has_coral():
                if self.__intake_input.get_button_up():
                    feed_coral = not feed_coral

                if feed_coral:
                    self.__conveyor.feed_coral(0.7)
                else:
                    self.__conveyor.feed_coral(0)

                yield None

            self.__coral_in_intake_event.set()
            self.__swerve.set_local_offset(math.pi)
            self.__conveyor.feed_coral(0)

            yield from self.__elevator.wait_for_height()
            yield from Timer.wait_parallel(
                self.__conveyor.send_coral(),
                self.__coral_outtake.feed_coral()
            )

            self.__elevator.set_stage(1)
            yield from self.__elevator.wait_for_height(0.005)

            self.__coral_in_elevator_event.set()

            self.reef_align()
            elevator_up = False
            while True:
                if self.__intake_input.get_button_up():
                    elevator_up = not elevator_up

                reef_height = ReefSelector.get_height()
                if elevator_up or reef_height == 1:
                    self.__elevator.set_stage(reef_height)

                    if self.__elevator.is_at_target(0.005):
                        self.__elevator_at_height_event.set()

                        if self.__outtake_input.get_button_up():
                            break
                else:
                    self.__elevator.set_stage(1)

                yield None

            yield from self.__coral_outtake.shoot_coral()
            self.__coral_shot_event.set()
            self.coral_station_align()
            yield from self.__intake_input.wait_until('up')
            yield None

    def __align_logic_loop__(self):
        selected_tag = None
        target_pos = None
        rotation_offset = 0.

        last_seen = 0
        last_align_target = None

        while True:
            if not self.__should_align:
                yield None
                continue

            # Is the currently selected tag is still valid
            if selected_tag is not None and (Timer.get_elapsed(last_seen) >= 0.5 or last_align_target != self.__align_target):
                selected_tag = None

            # If not tag is already selected. try to find a new target
            if selected_tag is None:
                if self.__align_target == AlignTarget.CORAL_STATION:
                    # Get all the detected coral station tag from the cam with id 1
                    tags = tags_from_cam(AprilTagsReefscapeField.get_coral_station().all, 1)
                    if len(tags) > 0:
                        selected_tag = tags[0]
                        target_pos = CORAL_STATION_TARGET
                elif self.__align_target == AlignTarget.REEF:
                    # Get all the detected reef tag from the cam with id 0
                    tags = tags_from_cam(AprilTagsReefscapeField.get_reef().all, 0)
                    if len(tags) > 0:
                        # Select the closest tag if multiple tags are detected
                        # selected_tag = min(tags, key=lambda k: k.relative_position.magnitude)
                        selected_tag = min(tags,
                                           key=lambda k: (k.center / Vector2(800., 652) - Vector2(0.5, 0.5)).magnitude)
                        rotation_offset = math.pi

                        # Align on the selected side of the reef
                        if ReefSelector.get_side() == 0:
                            target_pos = REEF_LEFT_TARGET
                        else:
                            target_pos = REEF_RIGHT_TARGET
                elif self.__align_target == AlignTarget.CUSTOM:
                    # Check if the tag is detected by the correct camera
                    if self.__align_tag.is_detected and self.__align_tag.nt.get_cam_id() == self.__align_cam_id:
                        selected_tag = self.__align_tag
                        rotation_offset = math.pi if self.__align_cam_id == 0 else 0
                        target_pos = self.__align_position

            if selected_tag is not None:
                last_seen = Timer.get_current_time()

                position = Vector2(selected_tag.relative_position.x, selected_tag.relative_position.z * 0.866)
                tag_angle = TARGET_ANGLES[selected_tag.id]

                if self.__target_position is None:
                    self.__target_position = position

                if selected_tag.is_detected:
                    self.__target_position = self.__target_position * 0.95 + target_pos * 0.05
                else:
                    self.__target_position = self.__target_position * 0.95 + position * 0.05

                error_angle = delta_angle(self.__swerve.get_heading(), tag_angle)
                error_position = position - self.__target_position

                real_error_position = position - target_pos
                if self.__target_error is None:
                    self.__target_error = real_error_position.magnitude

                self.__target_error = self.__target_error * 0.90 + real_error_position.magnitude * 0.1
                if approximately(self.__target_error, 0, 0.007) and approximately(error_angle, 0, 0.1):
                    self.__robot_aligned_event.set()

                # Apply Proportional gain
                translation = Vector2(error_position.x * 0.6,
                                      error_position.y * 0.6)
                rotation = error_angle * -0.10

                # Apply Feed Forward
                if error_position.magnitude <= 0.30:
                    min_x = abs(error_position.x) / (abs(error_position.x) + 0.05) * 0.26
                    min_y = abs(error_position.y) / (abs(error_position.y) + 0.05) * 0.26
                else:
                    min_x = 0
                    min_y = 0

                translation.x = math.copysign(max(min_x, abs(translation.x)), translation.x)
                translation.y = math.copysign(max(min_y, abs(translation.y)), translation.y)

                # Convert translation from local to world coordinate system
                translation = translation.rotate(self.__swerve.get_heading() + rotation_offset)

                # Apply commands to swerve drive
                self.__vertical_input.override(translation.x / self.__swerve_speed)
                self.__horizontal_input.override(translation.y / self.__swerve_speed)
                self.__rotation_input.override(rotation)
            else:
                self.__target_position = None
                self.__target_error = None

            yield None

    def __climb_logic_loop__(self):
        while True:
            yield from self.__climb_input.wait_until('up')
            yield from self.__climber.wait_for_angle(0.29)

            while True:
                climb_sum = 0

                if self.__manual_climber_down_input.get():
                    climb_sum -= 0.8
                if self.__manual_climber_up_input.get():
                    climb_sum += 0.2

                self.__climber.set_speed(climb_sum)

                yield None

            yield None

    def __recalibrate_logic_loop__(self):
        while True:
            yield from self.__recalibrate_input.wait_until('down')
            start_time = Timer.get_current_time()
            yield from self.__recalibrate_input.wait_until('up')

            if Timer.get_elapsed(start_time) >= 0.5:
                self.__swerve.set_current_heading(0)

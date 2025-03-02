import math

from frctools import RobotBase, WPI_CANSparkMax, WPI_CANSparkFlex
from frctools.sensor import Encoder
from frctools.drivetrain import SwerveModule, SwerveDrive, SwerveDriveMode
from frctools.controll import PID
from frctools.frcmath import Vector2, SlewRateLimiter
from frctools.input import Input, XboxControllerInput, PowerTransform
from frctools.vision.apriltags import AprilTagsReefscapeField

from robot2025 import Climber, Conveyor, CoralOuttake, Elevator, RobotController

from wpilib import DutyCycleEncoder, ADIS16448_IMU, SPI, DigitalInput


class Robot(RobotBase):
    def robotInit(self):
        super().robotInit()

        Input.add_axis('horizontal',
                       0,
                       XboxControllerInput.LEFT_JOYSTICK_Y,
                       deadzone=0.02,
                       axis_filter=SlewRateLimiter(100),
                       axis_transform=PowerTransform(1.5))
        Input.add_axis('vertical',
                       0,
                       XboxControllerInput.LEFT_JOYSTICK_X,
                       inverted=True,
                       deadzone=0.02,
                       axis_filter=SlewRateLimiter(100),
                       axis_transform=PowerTransform(1.5))

        Input.create_composite_axis('rotation',
                       positive=Input.add_axis('rotation_pos',
                                               0,
                                               XboxControllerInput.RIGHT_TRIGGER,
                                               deadzone=0.02,
                                               axis_transform=PowerTransform(1.5)),
                       negative=Input.add_axis('rotation_neg',
                                               0,
                                               XboxControllerInput.LEFT_TRIGGER,
                                               deadzone=0.02,
                                               axis_transform=PowerTransform(1.5)),
                       axis_filter=SlewRateLimiter(100))

        Input.add_button('align', 0, XboxControllerInput.X)
        Input.add_button('intake', 0, XboxControllerInput.A)
        Input.add_button('outtake', 0, XboxControllerInput.B)

        Input.add_button('manual_elevator_up', 0, XboxControllerInput.RB)
        Input.add_button('manual_elevator_down', 0, XboxControllerInput.LB)

        swerve_modules = [
            SwerveModule(drive_motor=WPI_CANSparkFlex(2, True, brake=True, inverted=True),
                         steering_motor=WPI_CANSparkMax(1, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(0), 0, False),
                         steering_controller=PID(0.3, 0, 0),
                         steering_offset=0.548,
                         position=Vector2(-10.875, 13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(8, True, brake=True),
                         steering_motor=WPI_CANSparkMax(7, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(3), 0, False),
                         steering_controller=PID(0.3, 0, 0),
                         steering_offset=0.821,
                         position=Vector2(-10.875, -13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(6, True, brake=True),
                         steering_motor=WPI_CANSparkMax(5, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(2), 0, False),
                         steering_controller=PID(0.3, 0, 0),
                         steering_offset=0.389,
                         position=Vector2(10.875, -13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(4, True, brake=True, inverted=True),
                         steering_motor=WPI_CANSparkMax(3, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(1), 0, False),
                         steering_controller=PID(0.3, 0, 0),
                         steering_offset=0.001,
                         position=Vector2(10.875, 13.375))
        ]

        swerve = SwerveDrive(swerve_modules, imu=ADIS16448_IMU(ADIS16448_IMU.IMUAxis.kZ, SPI.Port.kMXP, ADIS16448_IMU.CalibrationTime._1s), start_heading=math.pi)
        swerve.set_drive_mode(SwerveDriveMode.ROBOT_CENTRIC)
        swerve.set_cosine_compensation(True)
        self.add_component('Swerve', swerve)

        # climber = Climber()
        # self.add_component('Climber', climber)

        conveyor = Conveyor(WPI_CANSparkMax(11, True, True), DigitalInput(4))
        self.add_component('Conveyor', conveyor)

        coral_outtake = CoralOuttake(WPI_CANSparkMax(10, True, True), DigitalInput(5))
        self.add_component('CoralOuttake', coral_outtake)

        elevator = Elevator(WPI_CANSparkFlex(12, True, True), Encoder(DutyCycleEncoder(6), 0.42, False), PID(9, 0, 0, 0.015, integral_range=(-0.5, 0.5)), DigitalInput(8), DigitalInput(7))
        self.add_component('Elevator', elevator)

        controller = RobotController()
        self.add_component('RobotController', controller)

    def disabledExit(self):
        super().disabledExit()

        # Refresh the alliance for the april tags
        AprilTagsReefscapeField.refresh_alliance()

import math

from frctools import RobotBase, WPI_CANSparkMax, WPI_CANSparkFlex
from frctools.sensor import Encoder
from frctools.drivetrain import SwerveModule, SwerveDrive
from frctools.controll import PID
from frctools.frcmath import Vector2, SlewRateLimiter
from frctools.input import Input, XboxControllerInput, PowerTransform

from wpilib import DutyCycleEncoder, ADIS16448_IMU, SPI


class Robot(RobotBase):
    def robotInit(self):
        super().robotInit()

        self.__h = Input.add_axis('horizontal',
                       0,
                       XboxControllerInput.LEFT_JOYSTICK_Y,
                       deadzone=0.02,
                       axis_filter=SlewRateLimiter(1),
                       axis_transform=PowerTransform(1.5))
        Input.add_axis('vertical',
                       0,
                       XboxControllerInput.LEFT_JOYSTICK_X,
                       inverted=True,
                       deadzone=0.02,
                       axis_filter=SlewRateLimiter(1),
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
                       axis_filter=SlewRateLimiter(1.75))

        swerveModule = [
            SwerveModule(drive_motor=WPI_CANSparkFlex(2, True, brake=True, inverted=True),
                         steering_motor=WPI_CANSparkMax(1, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(0), 0, False),
                         steering_controller=PID(1, 0, 0),
                         steering_offset=0.548,
                         position=Vector2(-10.875, 13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(8, True, brake=True),
                         steering_motor=WPI_CANSparkMax(7, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(3), 0, False),
                         steering_controller=PID(1, 0, 0),
                         steering_offset=0.821,
                         position=Vector2(-10.875, -13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(6, True, brake=True),
                         steering_motor=WPI_CANSparkMax(5, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(2), 0, False),
                         steering_controller=PID(1, 0, 0),
                         steering_offset=0.389,
                         position=Vector2(10.875, -13.375)),

            SwerveModule(drive_motor=WPI_CANSparkFlex(4, True, brake=True, inverted=True),
                         steering_motor=WPI_CANSparkMax(3, True, brake=True),
                         steering_encoder=Encoder(DutyCycleEncoder(1), 0, False),
                         steering_controller=PID(1, 0, 0),
                         steering_offset=0.001,
                         position=Vector2(10.875, 13.375))
        ]

        swerve = SwerveDrive(swerveModule, imu=ADIS16448_IMU(ADIS16448_IMU.IMUAxis.kZ, SPI.Port.kMXP, ADIS16448_IMU.CalibrationTime._1s), start_heading=math.pi)

        self.add_component('Swerve', swerve)

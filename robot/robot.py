import math

from frctools import RobotBase, WPI_TalonFX, WPI_CANSparkMax
from frctools.drivetrain import SwerveDrive, SwerveModule
from frctools.frcmath import Vector2
from frctools.controll import PID
from frctools.vision.apriltags import AprilTagsNetworkTable

from wpilib import AnalogEncoder, ADIS16448_IMU, SPI


class Robot(RobotBase):
    def robotInit(self):
        super().robotInit()

        # Initialize AprilTags
        AprilTagsNetworkTable(16)

        try:
            swerve_modules = [
                SwerveModule(drive_motor=WPI_TalonFX(8, brake=True),
                             steering_motor=WPI_CANSparkMax(7, brushless=True, brake=True),
                             steering_encoder=AnalogEncoder(0),
                             steering_controller=PID(1, 0, 0),
                             steering_offset=0.964010-0.25,
                             position=Vector2(0.256, 0.312)),

                SwerveModule(drive_motor=WPI_TalonFX(6, brake=True),
                             steering_motor=WPI_CANSparkMax(5, brushless=True, brake=True),
                             steering_encoder=AnalogEncoder(1),
                             steering_controller=PID(1, 0, 0),
                             steering_offset=0.6943,
                             position=Vector2(0.256, -0.312)),

                SwerveModule(drive_motor=WPI_TalonFX(4, inverted=True, brake=True),
                             steering_motor=WPI_CANSparkMax(3, brushless=True, brake=True),
                             steering_encoder=AnalogEncoder(2),
                             steering_controller=PID(1, 0, 0),
                             steering_offset=0.3196,
                             position=Vector2(-0.256, -0.312)),

                SwerveModule(drive_motor=WPI_TalonFX(2, inverted=True, brake=True),
                             steering_motor=WPI_CANSparkMax(1, brushless=True, brake=True),
                             steering_encoder=AnalogEncoder(3),
                             steering_controller=PID(1, 0, 0),
                             steering_offset=0.9142,
                             position=Vector2(-0.256, 0.312)),
            ]

            swerve = SwerveDrive(modules=swerve_modules,
                                 imu=ADIS16448_IMU(ADIS16448_IMU.IMUAxis.kZ, SPI.Port.kMXP, ADIS16448_IMU.CalibrationTime._1s),
                                 start_heading=math.pi)

            self.add_component('Swerve', swerve)
        except Exception as e:
            print(e)

    def teleopPeriodic(self):
        super().teleopPeriodic()

        detected_tags = AprilTagsNetworkTable.get_detected()
        if len(detected_tags) > 0:
            print(detected_tags)

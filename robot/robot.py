from frctools import RobotBase, WPI_CANSparkMax
from frctools.input import Input, XboxControllerInput
from frctools.drivetrain import SwerveCalibratorModule, SwerveCalibrator

from wpilib import AnalogEncoder


class Robot(RobotBase):
    def robotInit(self):
        super().robotInit()

        Input.add_button('next_button', 0, XboxControllerInput.X)
        Input.create_composite_axis(
            name='drive',
            positive=Input.add_button('forward_drive', 0, XboxControllerInput.Y),
            negative=Input.add_button('backward_drive', 0, XboxControllerInput.X)
        )
        Input.create_composite_axis(
            name='direction',
            positive=Input.add_button('forward_dir', 0, XboxControllerInput.B),
            negative=Input.add_button('backward_dir', 0, XboxControllerInput.A)
        )

        self.calibrator = SwerveCalibrator(
            [
                SwerveCalibratorModule(WPI_CANSparkMax(2, True, True), WPI_CANSparkMax(1, True, True), AnalogEncoder(0)),
                SwerveCalibratorModule(WPI_CANSparkMax(8, True, True), WPI_CANSparkMax(7, True, True), AnalogEncoder(1)),
                SwerveCalibratorModule(WPI_CANSparkMax(6, True, True), WPI_CANSparkMax(5, True, True), AnalogEncoder(2)),
                SwerveCalibratorModule(WPI_CANSparkMax(4, True, True), WPI_CANSparkMax(3, True, True), AnalogEncoder(3)),
            ]
        )

    def teleopInit(self):
        self.calibrator.start()

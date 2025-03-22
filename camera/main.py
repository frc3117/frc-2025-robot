from cscore import CameraServer


cam = CameraServer.startAutomaticCapture()
CameraServer.waitForever()
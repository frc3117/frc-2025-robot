from frctools.vision import MjpegStreamer
from frctools.vision.apriltags import AprilTagsNetworkTable
from frc_apriltags import USBCamera, AprilTagDetector
from dotenv import load_dotenv

import time
import os
import ntcore


def parse_str(val: str) -> str:
    return val
def parse_bool(val: str) -> bool:
    return val.lower() == 'true'
def parse_int(val: str) -> int:
    return int(val)
def parse_tuple(val: str):
    val_split = val.split(',')
    return int(val_split[0]), int(val_split[1])


def environment_or_default(name: str, default, parser):
    value = os.environ.get(name)
    if value is None:
        return default

    return parser(value)


# Load environment variables from a .env file
load_dotenv(override=True)


# General settings
UNDISTORT_IMAGE = environment_or_default('FRC_UNDISTORT_IMAGE', True, parse_bool)

# CAM0 settings
CAM0_ID = environment_or_default('FRC_CAM0_ID', 0, parse_int)
CAM0_RESOLUTION = environment_or_default('FRC_CAM0_RESOLUTION', (1600, 1304), parse_tuple)
CAM0_FPS = environment_or_default('FRC_CAM0_FPS', 60, parse_int)
CAM0_CALIBRATION_FILE = environment_or_default('FRC_CAM0_CALIBRATION_FILE', 'calibration_0.json', parse_str)
CAM0_NAME = environment_or_default('FRC_CAM0_NAME', 'cam0', parse_str)

# CAM1 settings
CAM1_ID = environment_or_default('FRC_CAM1_ID', 2, parse_int)
CAM1_RESOLUTION = environment_or_default('FRC_CAM1_RESOLUTION', (1600, 1304), parse_tuple)
CAM1_FPS = environment_or_default('FRC_CAM1_FPS', 60, parse_int)
CAM1_CALIBRATION_FILE = environment_or_default('FRC_CAM1_CALIBRATION_FILE', 'calibration_1.json', parse_str)
CAM1_NAME = environment_or_default('FRC_CAM1_NAME', 'cam1', parse_str)

# NetworkTables settings
NT_IDENTITY = environment_or_default('FRC_NT_IDENTITY', 'april-tags-detector', parse_str)
NT_SERVER_ADDRESS = environment_or_default('FRC_NT_SERVER_ADDRESS', '10.31.17.2', parse_str)


def main():
    # Create the camera
    cam0 = USBCamera(CAM0_ID, CAM0_RESOLUTION, CAM0_FPS)
    cam1 = USBCamera(CAM1_ID, CAM1_RESOLUTION, CAM1_FPS)

    # Start the camera thread
    cam0.start()
    cam1.start()

    # Wait until the camera read its first frame
    cam0.wait_for_init()
    cam1.wait_for_init()

    # Create the mjpeg streamer
    streamer = MjpegStreamer()

    stream0_raw = streamer.create_stream(f'{CAM0_NAME}/raw', CAM0_FPS, CAM0_RESOLUTION)
    stream0_detection = streamer.create_stream(f'{CAM0_NAME}/detection', CAM0_FPS, CAM0_RESOLUTION)

    stream1_raw = streamer.create_stream(f'{CAM1_NAME}/raw', CAM1_FPS, CAM1_RESOLUTION)
    stream1_detection = streamer.create_stream(f'{CAM1_NAME}/detection', CAM1_FPS, CAM1_RESOLUTION)

    streamer.start()

    # Create the April Tag Detector
    detector0 = AprilTagDetector(stream0_raw, stream0_detection, CAM0_RESOLUTION, CAM0_CALIBRATION_FILE)
    detector1 = AprilTagDetector(stream1_raw, stream1_detection, CAM1_RESOLUTION, CAM1_CALIBRATION_FILE)

    # Create the network table client
    nt = ntcore.NetworkTableInstance.getDefault()
    nt.startClient4(NT_IDENTITY)
    nt.setServer(NT_SERVER_ADDRESS, ntcore.NetworkTableInstance.kDefaultPort4)

    april_tags_nt = AprilTagsNetworkTable(16, nt)

    # Initialize the last frame index
    cam0_last_index = -1
    cam1_last_index = -1

    # Initialize the current detection
    detection_0 = []
    detection_1 = []
    while True:
        # If any of the camera is not running close the program
        # If it is running as a service act as a reboot
        if not cam0.is_running() or not cam1.is_running():
            cam0.stop()
            cam1.stop()
            break

        new_frame = False

        # Get the new frames for the cameras
        frame0, frame0_index = cam0.get_frame()
        frame1, frame1_index = cam1.get_frame()

        # Process frame only if they are new
        if frame0_index > cam0_last_index:
            cam0_last_index = frame0_index
            new_frame = True
            detection_0 = detector0.detect(frame0, UNDISTORT_IMAGE)
        if frame1_index > cam1_last_index:
            cam1_last_index = frame1_index
            new_frame = new_frame
            detection_1 = detector1.detect(frame1, UNDISTORT_IMAGE)

        # If any new frame has been processed update the NetworkTables
        if new_frame:
            all_detection = []
            for d0 in detection_0:
                all_detection.append((0, d0))
            for d1 in detection_1:
                all_detection.append((1, d1))

            april_tags_nt(all_detection)
        else: # Sleep a bit if there is no new frame
            time.sleep(0.001)


if __name__ == '__main__':
    main()
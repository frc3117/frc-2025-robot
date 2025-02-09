from frctools.vision import MjpegStreamer
from frctools.vision.apriltags import AprilTagsNetworkTable
from frc_apriltags import USBCamera, AprilTagDetector

import time
import ntcore


CAM0_RESOLUTION = (1600, 1304)
CAM0_FPS = 60

CAM1_RESOLUTION = (1600, 1304)
CAM1_FPS = 60


def main():
    # Create the camera
    cam0 = USBCamera(0, CAM0_RESOLUTION, CAM0_FPS)
    cam1 = USBCamera(1, CAM1_RESOLUTION, CAM1_FPS)

    # Start the camera thread
    cam0.start()
    cam1.start()

    # Wait until the camera read its first frame
    cam0.wait_for_init()
    cam1.wait_for_init()

    # Create the mjpeg streamer
    streamer = MjpegStreamer()

    stream0_raw = streamer.create_stream('cam0/raw', CAM0_FPS, CAM0_RESOLUTION)
    stream0_detection = streamer.create_stream('cam0/detection', CAM0_FPS, CAM0_RESOLUTION)

    stream1_raw = streamer.create_stream('cam1/raw', CAM1_FPS, CAM1_RESOLUTION)
    stream1_detection = streamer.create_stream('cam1/detection', CAM1_FPS, CAM1_RESOLUTION)

    streamer.start()

    # Create the April Tag Detector
    detector0 = AprilTagDetector(stream0_raw, stream0_detection, CAM0_RESOLUTION, 'calibration_0.json')
    detector1 = AprilTagDetector(stream1_raw, stream1_detection, CAM1_RESOLUTION, 'calibration_1.json')

    # Create the network table client
    nt = ntcore.NetworkTableInstance.getDefault()
    nt.startClient4('april-tags-detector')
    nt.setServer('10.31.17.2', ntcore.NetworkTableInstance.kDefaultPort4)

    april_tags_nt = AprilTagsNetworkTable(16, nt)

    #
    cam0_last_index = -1
    cam1_last_index = -1

    detection_0 = []
    detection_1 = []
    while True:
        new_frame = False

        frame0, frame0_index = cam0.get_frame()
        frame1, frame1_index = cam1.get_frame()

        if frame0_index > cam0_last_index:
            cam0_last_index = frame0_index
            new_frame = True
            detection_0 = detector0.detect(frame0, True)
        if frame1_index > cam1_last_index:
            cam1_last_index = frame1_index
            new_frame = new_frame
            detection_1 = detector1.detect(frame1, True)

        if new_frame:
            all_detection = []
            for d0 in detection_0:
                all_detection.append((0, d0))
            for d1 in detection_1:
                all_detection.append((1, d1))

            april_tags_nt(all_detection)
        else:
            time.sleep(0.001)


if __name__ == '__main__':
    main()
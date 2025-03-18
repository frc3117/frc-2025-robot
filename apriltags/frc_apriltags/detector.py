import json
import numpy as np
import cv2 as cv
import pupil_apriltags as april_tags


def __draw_frustum__(img, translation, rotation, camera_params, tag_size, outline_color):
    camera_params = np.array(camera_params)
    dist_coeffs = np.zeros((4, 1))

    # 3D points of the bottom of the frustum
    bottom = np.array([
        [-tag_size / 2, tag_size / 2, 0],
        [tag_size / 2, tag_size / 2, 0],
        [tag_size / 2, -tag_size / 2, 0],
        [-tag_size / 2, -tag_size / 2, 0]
    ], dtype=np.float32)

    # 3D points of the top of the frustum
    top = np.array([
        [-tag_size / 2, tag_size / 2, -tag_size],
        [tag_size / 2, tag_size / 2, -tag_size],
        [tag_size / 2, -tag_size / 2, -tag_size],
        [-tag_size / 2, -tag_size / 2, -tag_size]
    ], dtype=np.float32)

    rotation = np.array(rotation)
    translation = np.array(translation)

    image_points_bottom, _ = cv.projectPoints(bottom, rotation, translation, camera_params, dist_coeffs)
    image_points_top, _ = cv.projectPoints(top, rotation, translation, camera_params, dist_coeffs)

    top_corner_points = []

    # Draw pillars from bottom points to top points
    for i in range(4):
        x1, y1 = image_points_bottom[i][0]
        x2, y2 = image_points_top[i][0]

        top_corner_points.append((x2, y2))

        cv.line(img, (int(x1), int(y1)), (int(x2), int(y2)), outline_color, 2)

    # Create a polyline for the top corners
    top_corners_temp = np.array(top_corner_points, dtype=np.int32)
    return cv.polylines(img, [top_corners_temp], isClosed=True, color=outline_color, thickness=2)


class AprilTagDetector:
    def __init__(self, raw_stream, detection_stream, resolution, calibration_file: str, tag_size: float = 0.165, tag_family: str = 'tag36h11'):
        self.__raw_stream = raw_stream
        self.__detection_stream = detection_stream
        self.__resolution = resolution

        with open(calibration_file, 'r') as f:
            json_calibration = json.load(f)

        # Load distortion coeficients
        dist_json = json_calibration['distortion']

        self.__dist = np.array([
            dist_json['k1'],
            dist_json['k2'],
            dist_json['p1'],
            dist_json['p2'],
            dist_json['k3']
        ], dtype=np.float32)

        # Load camera matrix
        mtx_json = json_calibration['matrix']

        # April Tags format
        self.__apriltags_camera_params = (
            mtx_json['fx'],
            mtx_json['fy'],
            mtx_json['cx'],
            mtx_json['cy']
        )

        #  OpenCV format
        self.__camera_matrix = np.array([
            [mtx_json['fx'], 0, mtx_json['cx']],
            [0, mtx_json['fy'], mtx_json['cy']],
            [0, 0, 1]
        ], dtype=np.float32)

        self.__new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self.__camera_matrix, self.__dist, resolution, 0, resolution)
        self.__mapx, self.__mapy = cv.initUndistortRectifyMap(self.__camera_matrix, self.__dist, None, self.__new_camera_matrix, resolution, 5)

        self.__detector = april_tags.Detector(families=tag_family, nthreads=16)
        self.__tag_size = tag_size

    def detect(self, frame, undistort=False):
        frame = cv.resize(frame, self.__resolution)
        if undistort:
            frame = cv.remap(frame, self.__mapx, self.__mapy, cv.INTER_LINEAR)

        detection_frame = frame.copy()
        gray_frame = frame[..., 2]

        # Detect tags
        detection_list = self.__detector.detect(gray_frame, estimate_tag_pose=True, camera_params=self.__apriltags_camera_params, tag_size=self.__tag_size)

        if self.__detection_stream is not None and self.__detection_stream.has_demand():
            tags_outline = []
            tags_center = []
            for detection in detection_list:
                # Get vertices for the outline of the tag
                points = np.array([[int(corners[0]), int(corners[1])] for corners in detection.corners],
                                  np.int32)
                points = points.reshape((-1, 1, 2))
                tags_outline.append(points)

                # Get center point of the tag
                center = np.array([[int(detection.center[0]), int(detection.center[1])]], np.int32)
                center = center.reshape((-1, 1, 2))
                tags_center.append(center)

                # Get the pose of the tag
                position = (detection.pose_t[0][0], detection.pose_t[1][0], detection.pose_t[2][0])
                rotation = detection.pose_R

                # Draw the bounding box of the tag
                detection_frame = __draw_frustum__(frame, position, rotation, self.__camera_matrix, self.__tag_size,
                                                 (0, 255, 0))

        self.__raw_stream.set_frame(frame)
        self.__detection_stream.set_frame(detection_frame)

        return detection_list

    def __call__(self, frame, undistort: bool = False):
        self.detect(frame, undistort)
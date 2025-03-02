import cv2 as cv
import numpy as np
import json


CALIBRATION_FILE = 'calibration_usb_reef_92.json'

RESOLUTION = (1600, 1304)
FPS = 60

CHESSBOARD_SIZE = (7, 10)

# Initialize the camera
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
cap.set(cv.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])
cap.set(cv.CAP_PROP_FPS, FPS)

# Termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1],3), np.float32)
objp[:,:2] = np.mgrid[0:CHESSBOARD_SIZE[0],0:CHESSBOARD_SIZE[1]].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

last_pressed = False
while True:
    ret, img = cap.read()
    if not ret:
        raise Exception('Error with camera')
    
    cv.imshow('preview', img)

    pressed_key = cv.waitKey(1) & 0xFF

    if pressed_key == ord('q'):
        break

    is_pressed = pressed_key == ord('p')
    if is_pressed and not last_pressed:
        gray_img = img[..., 2]

        ret, corners = cv.findChessboardCorners(gray_img, CHESSBOARD_SIZE, None)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray_img,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

            cv.drawChessboardCorners(img, CHESSBOARD_SIZE, corners2, ret)

        cv.imshow('calibration', img)

        last_pressed = True
    elif not is_pressed and last_pressed:
        last_pressed = False

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray_img.shape[::-1], None, None)

print(dist)
print(mtx)

calibration_json = {
    'distortion': {
        'k1': dist[0][0],
        'k2': dist[0][1],
        'p1': dist[0][2],
        'p2': dist[0][3],
        'k3': dist[0][4]
    },
    'matrix': {
        'fx': mtx[0, 0],
        'fy': mtx[1, 1],
        'cx': mtx[0, 2],
        'cy': mtx[1, 2]
    }
}

with open(CALIBRATION_FILE, 'w') as f:
    json.dump(calibration_json, f, indent=2)


new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(mtx, dist, RESOLUTION, 0, RESOLUTION)
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, new_camera_matrix, RESOLUTION, 5)
while True:
    ret, img = cap.read()
    if not ret:
        raise Exception('Error with camera')

    img = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

    cv.imshow('preview', img)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break



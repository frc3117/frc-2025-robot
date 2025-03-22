from threading import Thread
from typing import Tuple

import time
import cv2 as cv


class USBCamera:
    def __init__(self, id: int = 0, resolution: Tuple[int, int] = (1600, 1304), fps: int = 60, flip: int = None):
        self.__id = id
        self.__resolution = resolution
        self.__fps = fps
        self.__flip = flip

        self.__current_frame = None
        self.__current_frame_index = -1
        self.__thread: Thread = None
        self.__should_run = False

    def start(self):
        if self.__thread is None:
            self.__should_run = True
            self.__thread = Thread(target=self.__thread__, daemon=True)
            self.__thread.start()

    def stop(self):
        if self.__thread is not None:
            self.__should_run = False
            self.__thread.join()

    def is_running(self) -> bool:
        return self.__thread is not None and self.__thread.is_alive()

    def wait_for_init(self):
        while self.__current_frame is None:
            time.sleep(0.05)
            if not self.__thread.is_alive():
                raise Exception("USB camera is not running")

    def get_frame(self):
        return self.__current_frame, self.__current_frame_index

    def __thread__(self):
        try:
            cap = cv.VideoCapture(self.__id)
            cap.set(cv.CAP_PROP_FRAME_WIDTH, self.__resolution[0])
            cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.__resolution[1])
            cap.set(cv.CAP_PROP_FPS, self.__fps)

            while self.__should_run:
                ret, frame = cap.read()
                if not ret:
                    break

                if self.__flip is not None:
                    frame = cv.flip(frame, self.__flip)

                self.__current_frame = frame
                self.__current_frame_index += 1

            if cap.isOpened():
                cap.release()

            self.__current_frame = None
            self.__current_frame_index = -1
        except Exception as e:
            print(e)
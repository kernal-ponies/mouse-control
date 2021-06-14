import cv2
import Detector

WINDOW_NAME = "MouseControl"
PUPIL_THRESH = 42
PHASE = 0
# PHASES as of now
# PHASE 0: Pupils configuration
# PHASE 1: Eyes Calibration
# PHASE 2: Paint Mode


def dummy(val):
    pass

if __name__=="__main__":
    detector = Detector.CascadeDetector()

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_FULLSCREEN)
    cv2.createTrackbar("Eye Detection Threshold", WINDOW_NAME, 0, 255, dummy)
    cv2.setTrackbarPos("Eye Detection Threshold", WINDOW_NAME, PUPIL_THRESH)



    while True:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        detector.find_eyes(frame)
import cv2
import Detector
import GUI
import Homography

PUPIL_THRESH = 42
PHASE = 0

# PHASE 0: Pupils manual configuration
# PHASE 1: Eyes automated calibration
# PHASE 2: Mouse control

cursor_pos = [-1, -1]

if __name__ == '__main__':
    detector = Detector.CascadeDetector()
    gui = GUI.GUI()
    homo = Homography.Homography()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cv2.namedWindow('EyeCursor', cv2.WINDOW_FULLSCREEN)
    cv2.createTrackbar('Eye Detection Threshold', 'EyeCursor', 0, 255, gui.on_trackbar) # gui.ontrackbar is a dummy function
    cv2.setTrackbarPos('Eye Detection Threshold', 'EyeCursor', PUPIL_THRESH)

    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        detector.find_eyes(frame)

        if PHASE == 1:
            if homo.homography is not None:
                PHASE = 2
                detector.start_phase(2)
                gui.end_calibration()
            else:
                if gui.calib_step(detector.is_left_visible, detector.is_right_visible):
                    homo.save_calibration_position([detector.left_pupil, detector.right_pupil], gui.calibration_cursor_pos, gui.calibration_counter)
                if gui.phase == 2:
                    PHASE = 2
                    homo.calculate_homography()
                    detector.start_phase(2)
        elif PHASE == 2:
            cursor_pos = homo.get_cursor_pos([detector.left_pupil, detector.right_pupil])

        gui.make_window(frame, detector.get_images(), cursor_pos, detector.overlap_threshold)

        k = cv2.waitKey(33)
        if k == 27 & 0xFF == ord('q'):
            break
        elif k == 32:
            if PHASE < 2:
                if PHASE == 0:
                    if not detector.is_left_visible or not detector.is_right_visible:
                        gui.alert_box("Error", "Show both your eyes to the camera.")
                        detector.phase -= 1
                        gui.phase -= 1
                        PHASE -= 1
                    else:
                        gui.alert_box("Calibration Phase", "Keep still your shoulders and follow the circle with "
                                                           "the eyes, moving with your head as more as possibile.")
                        cv2.destroyWindow("EyeCursor")
                        cv2.namedWindow('EyeCursor', cv2.WINDOW_FULLSCREEN)
                        gui.run_calibration_phase()
                detector.phase += 1
                gui.phase += 1
                PHASE += 1
        elif k == 60:  # < => decrease sensibility
            detector.overlap_threshold -= 0.01
        elif k == 62:  # > => increase sensibility
            detector.overlap_threshold += 0.01
        elif k == 105:  # i => Info on sensibility
            gui.alert_box("Info - Sensibility", "Set the eyes detector sensibility: stop when the purple squares around the eyes are "
                          "stable but also they keep following the eyes smoothly.")

        if PHASE == 1:
            if k == 116:  # t => Info on threshold
                gui.alert_box("Info - Threshold", "Set the pupils detector sensibility: stop when eyes and pupils are stably seen and "
                          "drawn.")


    cap.release()
    cv2.destroyAllWindows()

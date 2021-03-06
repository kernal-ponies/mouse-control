import numpy as np
import cv2
import os
import ctypes
import operator
import pyautogui

HEIGHT_CONST = 0.024
WIDTH_CONST = 0.032

class GUI:
    def __init__(self):
        self.screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        img = np.random.randint(222, size=(self.screensize[1], self.screensize[0], 3))
        self.canvas = np.array(img, dtype=np.uint8)
        self.canvas_tmp = np.array(img, dtype=np.uint8)
        self.canvas_w = self.canvas.shape[1] - int(self.screensize[0] * 0.2)
        self.canvas_h = self.canvas.shape[0]
        self.eye_radius = int(0.025 * self.canvas_w)
        self.phase = 0
        self.calibration_cursor_color = (0, 0, 255)
        self.waiting = False
        self.save_pos = False
        self.wait_count = 0
        self.step_w = int(WIDTH_CONST * self.canvas_w)
        self.step_h = int(HEIGHT_CONST * self.canvas_h)
        self.calibration_cursor_pos = (self.eye_radius, int(0.025 * self.canvas_h))
        self.last_calibration_checkpoint = -1
        self.calibration_counter = 0
        self.offset_y = (self.step_w - self.step_h) if self.step_w > self.step_h else (self.step_h - self.step_w)
        self.calibration_poses = [
            (self.step_w, self.step_h), (20 * self.step_w, self.step_h), (39 * self.step_w, self.step_h),
            (self.step_w, 20 * self.step_h), (20 * self.step_w, 20 * self.step_h), (39 * self.step_w, 20 * self.step_h),
            (self.step_w, 39 * self.step_h), (20 * self.step_w, 39 * self.step_h), (39 * self.step_w, 39 * self.step_h),
            (10 * self.step_w, self.step_h), (30 * self.step_w, self.step_h),
            (10 * self.step_w, 20 * self.step_h), (30 * self.step_w, 20 * self.step_h),
            (10 * self.step_w, 39 * self.step_h), (30 * self.step_w, 39 * self.step_h),
            (self.step_w, 30 * self.step_h), (39 * self.step_w, 10 * self.step_h),
        ]
        self.cursor_radius = 10
        self.cursor_color = (0, 0, 0)
        self.prev_left_eye_frame_coordinates = np.random.randint(0, 5, size=(81, 81, 3))
        self.prev_right_eye_frame_coordinates = np.random.randint(0, 5, size=(81, 81, 3))
        self.blink_count_timeout = 0


    def on_trackbar(self, val):
        pass

    def make_window(self, main_image, lateral_images, cursor=None, sensibility=0.95):

        ratio = main_image.shape[1] / main_image.shape[0]

        img = np.random.randint(222, size=(self.screensize[1], self.screensize[0], 3))
        img = np.array(img, dtype=np.uint8)

        main_height = int(self.screensize[1] * 0.8)
        main_width = int(main_height * ratio)

        face_frame_coordinates = lateral_images["face_frame_coordinates"]
        left_eye_frame_coordinates = lateral_images["left_eye_frame_coordinates"]
        right_eye_frame_coordinates = lateral_images["right_eye_frame_coordinates"]
        lp_frame_coordinates = lateral_images["lp_frame_coordinates"]
        rp_frame_coordinates = lateral_images["rp_frame_coordinates"]

        # Main image
        if self.phase == 0:
            main_y_offset = int((self.screensize[1] - main_height) / 3)
            main_x_offset = int((self.screensize[0] - main_width) / 4)
            main_image = cv2.resize(main_image, (main_width, main_height))

            img[main_y_offset:main_image.shape[0] + main_y_offset,
            main_x_offset:main_image.shape[1] + main_x_offset] = main_image
            # Instruction
            img[0:main_y_offset, main_x_offset:main_image.shape[1] + main_x_offset] = cv2.blur(
                img[0:main_y_offset, main_x_offset:main_image.shape[1] + main_x_offset], (10, 10))
            img = cv2.putText(img, 'Adjust the threshold, then press space to calibrate [t for info]',
                              (main_x_offset + 10, int(main_y_offset / 2)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, color=(255, 255, 255))
        else:
            img = self.canvas

            if self.phase == 2:
                img = cv2.copyTo(self.canvas_tmp, None)

        # Lateral Bar
        lateral_width = int(self.screensize[0] * 0.2)
        lateral_height = self.screensize[1]
        if self.phase != 1:
            img[0:img.shape[0], img.shape[1] - lateral_width:img.shape[1]] = (77, 77, 77)

        
        if self.phase != 1:
            # Face Zoom Image
            if face_frame_coordinates is not None:
                im1_width = int(lateral_width * 0.8)
                im1_height = int(im1_width / ratio)
                im1_x_offset = int(lateral_width * 0.1)
                face_frame_coordinates = cv2.resize(face_frame_coordinates, (im1_width, im1_height))
                img[40:face_frame_coordinates.shape[0] + 40,
                img.shape[1] - lateral_width + im1_x_offset: img.shape[
                                                                1] - lateral_width + im1_x_offset + im1_width] = \
                    face_frame_coordinates
                img = cv2.putText(img, 'Face', (img.shape[1] - lateral_width + int(lateral_width / 2) - 25, 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color=(242, 242, 242))

        if self.phase == 0:
            # Left Eye Image
            if left_eye_frame_coordinates is not None:
                im2_width = int(lateral_width * 0.3)
                im2_height = im2_width
                im2_x_offset = int(lateral_width * 0.15)
                im2_y_offset = int(lateral_width * 0.45)
                left_eye_frame_coordinates = cv2.resize(left_eye_frame_coordinates, (im2_width, im2_height))
                img[left_eye_frame_coordinates.shape[0] + 65 + im2_y_offset:2 * left_eye_frame_coordinates.shape[0] + 65 + im2_y_offset,
                img.shape[1] - lateral_width + im2_x_offset: img.shape[1] - lateral_width + im2_x_offset + im2_width] = left_eye_frame_coordinates

            # Right Eye Image
            if right_eye_frame_coordinates is not None:
                im3_width = int(lateral_width * 0.3)
                im3_height = im3_width  # int(im3_width / ratio)
                im3_x_offset = int(lateral_width * 0.6)
                im3_y_offset = int(lateral_width * 0.45)
                right_eye_frame_coordinates = cv2.resize(right_eye_frame_coordinates, (im3_width, im3_height))
                img[right_eye_frame_coordinates.shape[0] + 65 + im3_y_offset:2 * right_eye_frame_coordinates.shape[0] + 65 + im3_y_offset,
                img.shape[1] - lateral_width + im3_x_offset: img.shape[1] - lateral_width + im3_x_offset + im3_width] =  right_eye_frame_coordinates

            if left_eye_frame_coordinates is not None or right_eye_frame_coordinates is not None:
                img = cv2.putText(img, 'Eyes',
                                  (img.shape[1] - lateral_width + int(lateral_width / 2) - 25,
                                   face_frame_coordinates.shape[0] + 105),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.75, color=(242, 242, 242))

            # Left Pupil Keypoints Image
            if lp_frame_coordinates is not None:
                im6_width = int(lateral_width * 0.3)
                im6_height = im6_width  # int(im6_width / ratio)
                im6_x_offset = int(lateral_width * 0.15)
                im6_y_offset = int(lateral_width * 0.45)
                lp_frame_coordinates = cv2.resize(lp_frame_coordinates, (im6_width, im6_height))
                img[lp_frame_coordinates.shape[0] + 165 + im6_y_offset:2 * lp_frame_coordinates.shape[0] + 165 + im6_y_offset,
                img.shape[1] - lateral_width + im6_x_offset: img.shape[
                                                                 1] - lateral_width + im6_x_offset + im6_width] = \
                    lp_frame_coordinates

            # Right Pupil Keypoints Image
            if rp_frame_coordinates is not None:
                im7_width = int(lateral_width * 0.3)
                im7_height = im7_width  # int(im3_width / ratio)
                im7_x_offset = int(lateral_width * 0.6)
                im7_y_offset = int(lateral_width * 0.45)
                rp_frame_coordinates = cv2.resize(rp_frame_coordinates, (im7_width, im7_height))
                img[rp_frame_coordinates.shape[0] + 165 + im7_y_offset:2 * rp_frame_coordinates.shape[0] + 165 + im7_y_offset,
                img.shape[1] - lateral_width + im7_x_offset: img.shape[
                                                                 1] - lateral_width + im7_x_offset + im7_width] = \
                    rp_frame_coordinates

        if self.phase > 0:
            # if cursor position is inside the screem
            if cursor is not None and cursor[0] >= 0 and cursor[1] >= 0 and pyautogui.onScreen(cursor[0], cursor[1]):
                # move the mouse to cursor position
                pyautogui.moveTo(cursor)

        if self.phase == 2:
            left_eye_close = np.array_equal(left_eye_frame_coordinates, self.prev_left_eye_frame_coordinates) and not np.array_equal(right_eye_frame_coordinates, self.prev_right_eye_frame_coordinates)
            right_eye_close = np.array_equal(right_eye_frame_coordinates, self.prev_right_eye_frame_coordinates) and not np.array_equal(left_eye_frame_coordinates, self.prev_left_eye_frame_coordinates)
            if left_eye_close and self.blink_count_timeout == 0:
                # left click
                pyautogui.click(button = 'left')
                self.blink_count_timeout = 5
                print("clicked left")
            elif right_eye_close and self.blink_count_timeout == 0:
                # right click
                pyautogui.click(button = 'right')
                self.blink_count_timeout = 5
                print("clicked right")

        if self.phase != 1:
            # Sensibility Value
            img = cv2.putText(img, 'Sensibility',
                            (img.shape[1] - lateral_width + int(lateral_width / 2) - 55,
                            lateral_height - 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, color=(242, 242, 242))
            img = cv2.putText(img, "{:.2f}".format(sensibility),
                            (img.shape[1] - lateral_width + int(lateral_width / 2) - 15,
                            lateral_height - 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, color=(255, 255, 255))
            img = cv2.putText(img, 'Press  < to decrease',
                            (img.shape[1] - lateral_width + 10,
                            lateral_height - 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(242, 242, 242))
            img = cv2.putText(img, 'and > to increase, press i for info',
                            (img.shape[1] - lateral_width + 10,
                            lateral_height - 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(242, 242, 242))

        self.prev_left_eye_frame_coordinates = left_eye_frame_coordinates
        self.prev_right_eye_frame_coordinates = right_eye_frame_coordinates
        
        if self.blink_count_timeout > 0:
            self.blink_count_timeout -= 1

        cv2.imshow('EyeCursor', img)

    def run_calibration_phase(self):
        self.canvas[:, :] = (255, 255, 255)
        self.wait_count = 0
        self.calibration_cursor_pos = (15 * self.step_w, 15 * self.step_h + self.offset_y)
        self.step_w *= -1
        self.step_h *= -1

    def calib_step(self, left_visible=False, right_visible=False):
        eyes_visible = left_visible and right_visible
        # if eyes are not visible, turn the color to red, otherwise green
        self.calibration_cursor_color = (0, 255, 0) if eyes_visible else (0, 0, 255)

        if eyes_visible:
            if self.waiting:
                self.wait_count += 1
                self.calibration_cursor_color = (255, 0, 0)
                if self.wait_count == 10:
                    self.wait_count = 0
                    self.waiting = False
                    self.save_pos = False
            else:
                self.calibration_cursor_pos = (
                    list(self.calibration_cursor_pos)[0] + self.step_w,
                    list(self.calibration_cursor_pos)[1] + self.step_h)
                self.check_position()

        self.draw_calibration_canvas()
        self.canvas = cv2.circle(self.canvas, self.calibration_cursor_pos, self.eye_radius,
                                 self.calibration_cursor_color, -1)
        return self.save_pos

    def check_position(self):
        pos_x = int(list(self.calibration_cursor_pos)[0])
        pos_y = int(list(self.calibration_cursor_pos)[1]) - self.offset_y
        pos = (pos_x, pos_y)
        if pos in self.calibration_poses:
            self.save_pos = True if not self.save_pos else False
            self.calibration_cursor_color = (255, 0, 0)
            self.last_calibration_checkpoint += 1
            if not self.waiting:
                self.calibration_counter += 1
                self.waiting = True
            if pos == self.calibration_poses[0]:
                self.step_h = 0
                self.step_w = int(WIDTH_CONST * self.canvas_w)
            elif pos == self.calibration_poses[2]:
                self.step_h = int(HEIGHT_CONST * self.canvas_h)
                self.step_w = 0
            elif pos == self.calibration_poses[5]:
                self.step_h = 0
                self.step_w = -int(WIDTH_CONST * self.canvas_w)
            elif pos == self.calibration_poses[3]:
                self.step_h = int(HEIGHT_CONST * self.canvas_h)
                self.step_w = 0
            elif pos == self.calibration_poses[6]:
                self.step_h = 0
                self.step_w = int(WIDTH_CONST * self.canvas_w)
            elif pos == self.calibration_poses[8]:
                self.step_h = 0
                self.step_w = 0
                self.end_calibration()

    def end_calibration(self):
        self.phase = 2
        self.canvas[:, :] = np.array(np.zeros(self.canvas.shape), dtype=np.uint8)
        self.canvas_tmp[:, :] = (255, 255, 255)

    def alert_box(self, title, message):
        ctypes.windll.user32.MessageBoxW(0, message, title, 1)

    def draw_calibration_canvas(self):
        self.canvas[:, :] = (255, 255, 255)
        # Draw the path
        sp = int(self.cursor_radius)
        checkpoint_poses = [tuple(map(operator.add, e, (sp, sp))) for e in self.calibration_poses]
        self.canvas = cv2.line(self.canvas, checkpoint_poses[0], checkpoint_poses[2], (133, 133, 133),
                               self.cursor_radius)
        self.canvas = cv2.line(self.canvas, checkpoint_poses[3], checkpoint_poses[5], (133, 133, 133),
                               self.cursor_radius)
        self.canvas = cv2.line(self.canvas, checkpoint_poses[6], checkpoint_poses[8], (133, 133, 133),
                               self.cursor_radius)
        self.canvas = cv2.line(self.canvas, checkpoint_poses[2], checkpoint_poses[5], (133, 133, 133),
                               self.cursor_radius)
        self.canvas = cv2.line(self.canvas, checkpoint_poses[3], checkpoint_poses[6], (133, 133, 133),
                               self.cursor_radius)

        checkpoint_color = (111, 111, 111)
        for checkpoint in self.calibration_poses:
            cv2.rectangle(self.canvas, checkpoint, tuple(map(operator.add, checkpoint, (20, 20))), checkpoint_color, -1)

        if self.last_calibration_checkpoint < 0:
            return

        sorted_indices = [0, 9, 1, 10, 2, 16, 5, 12, 4, 11, 3, 15, 6, 13, 7, 14, 8]
        sorted_poses = [self.calibration_poses[idx] for idx in sorted_indices]

        checkpoint_color = (0, 250, 0)
        cv2.rectangle(self.canvas, sorted_poses[0], tuple(map(operator.add, sorted_poses[0], (20, 20))), checkpoint_color,
                      -1)
        for square_idx in range(self.last_calibration_checkpoint):
            prev_square = sorted_poses[square_idx]
            square = sorted_poses[square_idx + 1]
            cv2.rectangle(self.canvas, prev_square, tuple(map(operator.add, prev_square, (20, 20))), checkpoint_color,
                          -1)
            cv2.rectangle(self.canvas, square, tuple(map(operator.add, square, (20, 20))), checkpoint_color, -1)
            self.canvas = cv2.line(self.canvas, tuple(map(operator.add, prev_square, (10, 10))), tuple(map(operator.add, square, (10, 10))), checkpoint_color, self.cursor_radius)
        self.canvas = cv2.line(self.canvas, tuple(map(operator.add, sorted_poses[self.last_calibration_checkpoint], (10, 10))), tuple(map(operator.add, self.calibration_cursor_pos, (10, 10))),
                               checkpoint_color, self.cursor_radius)

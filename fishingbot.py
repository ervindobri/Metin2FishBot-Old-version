import numpy as np
import pydirectinput
import cv2 as cv
import math
from time import time
from windowcapture import WindowCapture
import constants

class FishingBot:

    #properties
    fish_pos_x = None
    fish_pos_y = None
    fish_last_time = None
    detect_text_enable = False
    botting = False

    FISH_RANGE = 74
    FISH_VELO_PREDICT = 30

    # BAIT_POSITION = (473, 750)
    # FISH_POSITION = (440, 750)

    FILTER_CONFIG = [49, 0, 58, 134, 189, 189, 0, 0, 0, 0]

    FISH_WINDOW_CLOSE = (430, 115)

    # set position of the fish windows
    # this value can be diferent by the sizes of the game window

    FISH_WINDOW_SIZE = (280, 226)
    FISH_WINDOW_POSITION = (95, 80)

    wincap = None

    # Load the needle image

    needle_img = cv.imread('images/balloon.jpg', cv.IMREAD_UNCHANGED)
    needle_img_clock = cv.imread('images/clock.jpg', cv.IMREAD_UNCHANGED)

    # Some time cooldowns

    detect_text = True

    # Limit time

    initial_time = None

    end_time_enable = False

    end_time = 0

    # for fps

    loop_time = time()

    # The mouse click cooldown

    timer_mouse = time()

    # The timer beteween the states

    timer_action = time()

    bait_time = 2
    throw_time = 2
    pull_time = 2 # Pulling after detecting 2sec
    game_time = 2
    detect_threshold = 0.42
    not_detected_time = 30

    # # This is the filter parameters, this help to find the right image
    # hsv_filter = HsvFilter(*FILTER_CONFIG)

    state = 0

    def detect(self, haystack_img):

        # match the needle_image with the hasytack image
        result = cv.matchTemplate(haystack_img, self.needle_img, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        # needle_image's dimensions
        needle_w = self.needle_img.shape[1]
        needle_h = self.needle_img.shape[0]

        # get the position of the match image
        top_left = max_loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)

        # Draw the circle of the fish limits
        cv.circle(haystack_img,
                (int(haystack_img.shape[1] / 2), int(haystack_img.shape[0] / 2)),
                self.FISH_RANGE, color=(0, 0, 255), thickness=1)

        # Only the max level of match is greater than 0.5
        print("Detection percent: ", max_val)
        if max_val > self.detect_threshold:
            return True
        return None

    def detect_daily_reward(self, image):

        for i in range(0, 5):
            for j in range(0, 5):
                if image[10 + i,10 +  j, 0] + image[10 + i,10 +  j, 1] + image[10 + i,10 +  j, 2] > 0:
                    return False

        return True

    def set_to_begin(self, values):

        if values['-ENDTIMEP-']:
            self.end_time_enable = True
            try:
                self.end_time  = int(values['-ENDTIME-'])*60
            except:
                self.end_time = 0

        self.bait_time = values['-BAITTIME-']
        self.throw_time = values['-THROWTIME-']
        self.pull_time = float(values['-PULLTIME-'])
        self.game_time = values['-STARTGAME-']
        game_name = values['-GAMENAME-']
        print(game_name)

        self.wincap = WindowCapture(game_name)
        self.state = 0
        self.initial_time = time()
        self.timer_action = time()

        mouse_x = int(self.FISH_WINDOW_POSITION[0] + self.wincap.offset_x + 200)
        mouse_y = int(self.FISH_WINDOW_POSITION[1] + self.wincap.offset_y + 200)

        pydirectinput.click(x=mouse_x, y=mouse_y, button='right')

    def runHack(self):
        self.loop_time = time()
        screenshot = self.wincap.get_screenshot()
        print("State - ", self.state)
        
        # Verify total time
        if self.end_time_enable and time() - self.initial_time > self.end_time:
            self.botting = False

        # State to click put the bait in the rod
        if self.state == 0:

            if time() - self.timer_action > self.bait_time:
                self.detect_text = True
                pydirectinput.keyDown('2')
                pydirectinput.keyUp('2')
                self.state = 1
                self.timer_action = time()

        # State to throw the bait
        if self.state == 1:
            if time() - self.timer_action > self.throw_time:
                pydirectinput.keyDown('1')
                pydirectinput.keyUp('1')
                self.state = 2
                self.timer_action = time()


        # Wait until it's detected or timer runs out
        if self.state == 2:
            # detect balloon
            detected = self.detect(screenshot)
            print("DETECTED:", detected)
            if detected:
                self.state = 3
                self.timer_action = time()
            else:
                if time() - self.timer_action > self.not_detected_time:
                    self.state = 0
                    self.timer_action = time()

            # elif time() - self.timer_action > self.game_time*30:
            #     self.state = 0
            #     self.timer_action = time()


        # Pulling out the fishing rod
        if self.state == 3:
            if time() - self.timer_action >= self.pull_time:
                print("Pulling out!")
                pydirectinput.keyDown('1')
                pydirectinput.keyUp('1')
                self.state = 0
                self.timer_action = time()
            

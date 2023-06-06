'''
Turn on Camera on Zoom
'''

import os
import time

import pyautogui
import pywinauto

from info import CONFERENCE_NAME, IMAGE_START

class TurnOnCamera:
    'A class that turns on Camera on Zoom'

    def __init__(self):
        'initialize'
        self.image = os.path.join(os.getcwd(), 'images', IMAGE_START)
        self.pywinauto_app = pywinauto.Application()

    def connect(self):
        'connect to Zoom conference'
        self.pywinauto_app.connect(best_match=CONFERENCE_NAME).top_window().set_focus()

    def get_start_video_button(self):
        'get pos of start video'
        pos = pyautogui.locateOnScreen(self.image, confidence=0.7)
        if not pos:
            pyautogui.press('alt')
            time.sleep(0.1)
            pos = pyautogui.locateOnScreen(self.image, confidence=0.7)

        return pos

    def press_start_video_button(self, pos):
        'press start video'
        pyautogui.click(pos)

    def run(self):
        'run the whole process'
        self.connect()
        pos = self.get_start_video_button()
        if pos:
            self.press_start_video_button(pos)
        else:
            print("can't find the button")

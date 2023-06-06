'''
Turn on Camera on Zoom
'''

import time

import pyautogui
import pywinauto

from helper import get_last_match
from settings import CONFERENCE_NAME, START_IMAGE

class TurnOnCamera:
    'A class that turns on Camera on Zoom'

    def __init__(self):
        'initialize'
        self.image = START_IMAGE
        self.pywinauto_app = pywinauto.Application()

    def connect(self):
        'connect to Zoom conference'
        self.pywinauto_app.connect(best_match=CONFERENCE_NAME).top_window().set_focus()

    def get_start_video_button(self):
        'get pos of start video'
        pos = get_last_match(self.image)
        if pos == (0,0,0,0):
            pyautogui.press('alt')
            time.sleep(0.1)
            pos = get_last_match(self.image)

        return pos

    def press_start_video_button(self, pos):
        'press start video'
        pyautogui.click(pos)

    def run(self):
        'run the whole process'
        print('비디오 시작 스크립트 실행')
        self.connect()
        pos = self.get_start_video_button()
        if pos != (0,0,0,0):
            self.press_start_video_button(pos)
            print('비디오 시작')
        else:
            print('비디오 시작 버튼 찾을 수 없음')

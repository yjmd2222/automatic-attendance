'''
Turn on video on Zoom
'''

import pyautogui
import pywinauto

from settings import CONFERENCE_NAME, START_IMAGE

class TurnOnCamera:
    'A class that turns on video on Zoom'

    def __init__(self):
        'initialize'
        self.image = START_IMAGE
        self.pywinauto_app = pywinauto.Application()

    def connect(self):
        'connect to Zoom conference'
        self.pywinauto_app.connect(best_match=CONFERENCE_NAME).top_window().set_focus()

    def start_video_shortcut(self):
        'start video via shortcut'
        pyautogui.hotkey('alt', 'v')

    def run(self):
        'run the whole process'
        print('비디오 시작 스크립트 실행')
        self.connect()
        self.start_video_shortcut()
        print('비디오 시작 스크립트 완료')

if __name__ == '__main__':
    TurnOnCamera().run()
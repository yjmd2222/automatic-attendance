'''
Quit Zoom
'''

import os
import sys
import pywinauto
import win32gui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
# pylint: enable=wrong-import-position

class QuitZoom:
    'A class for quitting Zoom'

    def __init__(self):
        'initialize'
        self.pywinauto_app = pywinauto.Application()

    def connect_and_kill(self):
        'connect to Zoom conference and kill'
        hwnd_zoom_class_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
        if win32gui.IsWindowVisible(hwnd_zoom_class_classroom):
            self.pywinauto_app.connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)\
                .kill(soft=True)
            print('Zoom 회의 입장 확인 후 종료함')
        else:
            print('Zoom 회의 입장 안 함')

    def run(self):
        'Run the launch'
        print('줌 종료 스크립트 시작')
        self.connect_and_kill()

if __name__ == '__main__':
    QuitZoom().run()

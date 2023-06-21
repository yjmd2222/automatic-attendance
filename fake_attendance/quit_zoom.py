'''
Quit Zoom
'''

import os
import sys
import pywinauto
import win32gui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import print_with_time
from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
# pylint: enable=wrong-import-position

class QuitZoom:
    'A class for quitting Zoom'

    def connect_and_kill(self, pywinauto_app):
        'connect to Zoom conference and kill'
        hwnd_zoom_class_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
        if win32gui.IsWindowVisible(hwnd_zoom_class_classroom):
            pywinauto_app.connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)\
                .kill(soft=True)
            print_with_time('Zoom 회의 입장 확인 후 종료함')
        else:
            print_with_time('Zoom 회의 입장 안 함')

    def run(self):
        'Run the launch'
        pywinauto_app = pywinauto.Application()
        print_with_time('줌 종료 스크립트 시작')
        self.connect_and_kill(pywinauto_app)

if __name__ == '__main__':
    QuitZoom().run()

'''
Quit Zoom
'''

import os
import sys
import pywinauto
from pywinauto.findwindows import ElementNotFoundError

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.abc import BaseClass
from fake_attendance.helper import print_with_time
from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
# pylint: enable=wrong-import-position

class QuitZoom(BaseClass):
    'A class for quitting Zoom'

    def __init__(self):
        self.print_name = '줌 종료'
        super().__init__()

    def connect_and_kill(self, force):
        'connect to Zoom conference and kill'
        try:
            pywinauto.Application().connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)\
                .kill(soft=True)
            if force:
                print_with_time('숨겨진 Zoom 회의 종료')
            else:
                print_with_time('Zoom 회의 입장 확인 후 종료')
            return True
        except ElementNotFoundError:
            if force:
                print_with_time('숨겨진 Zoom 회의 없음')
            else:
                print_with_time('Zoom 회의 입장 안 함')
            return False

    def run(self, force=False):
        'Run the launch'
        self.connect_and_kill(force)

if __name__ == '__main__':
    QuitZoom().run()

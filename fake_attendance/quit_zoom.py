'''
Quit Zoom
'''

import os
from sys import platform

if platform == 'win32':
    import pywinauto
    from pywinauto.findwindows import ElementNotFoundError
else:
    import subprocess

from fake_attendance.abc import BaseClass
from fake_attendance.helper import print_with_time
from fake_attendance.notify import PrepareSendEmail
if platform == 'win32':
    from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
else:
    from fake_attendance.settings import ZOOM_APPLICATION_NAME

class QuitZoom(PrepareSendEmail, BaseClass):
    'A class for quitting Zoom'
    print_name = '줌 종료'

    def __init__(self):
        'initialize'
        PrepareSendEmail.define_attributes(self)
        PrepareSendEmail.decorate_run(self)
        BaseClass.__init__(self)

    def reset_attributes(self):
        'reset attributes for next run'
        PrepareSendEmail.define_attributes(self)

    def _kill_zoom_win32(self, kill_hidden):
        'kill Zoom conference on win32'
        for _ in range(3):
            try:
                pywinauto.Application().connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)\
                    .kill(soft=True)
                if kill_hidden:
                    print_with_time('숨겨진 Zoom 회의 종료')
                else:
                    print_with_time('Zoom 회의 입장 확인 후 종료')
                # set flag to quit content
                if not self.result_dict['quit']['content']:
                    self.result_dict['quit']['content'] = True
            except ElementNotFoundError:
                if kill_hidden:
                    print_with_time('숨겨진 Zoom 회의 없음')
                else:
                    print_with_time('실행 중인 Zoom 회의 없음')
                # set flag to quit content (nothing closed)
                if self.result_dict['quit']['content'] is None:
                    self.result_dict['quit']['content'] = False
                break

    def _kill_zoom_darwin(self, kill_hidden):
        'kill Zoom conference on darwin'
        applescript_code = f'''
        tell application "System Events"
            set theID to (unix id of processes whose name is "{ZOOM_APPLICATION_NAME}")
            try
                do shell script "kill -9 " & theID
            end try
        end tell'''

        with open(os.devnull, 'wb') as devnull:
            try:
                subprocess.run(['osascript', '-e', applescript_code],
                            stdout=devnull,
                            check=True)
                if kill_hidden:
                    print_with_time('숨겨진 Zoom 회의 포함 Zoom 애플리케이션 종료')
                else:
                    print_with_time('Zoom 애플리케이션 종료')
                # set flag to quit content
                self.result_dict['quit']['content'] = True
            except subprocess.CalledProcessError:
                if kill_hidden:
                    print_with_time('숨겨진 Zoom 회의 없음')
                else:
                    print_with_time('실행 중인 Zoom 애플리케이션 없음')
                # set flag to quit content (nothing closed)
                if self.result_dict['quit']['content'] is None:
                    self.result_dict['quit']['content'] = False

    def kill_zoom(self, kill_hidden):
        'kill Zoom conference'
        if platform == 'win32':
            self._kill_zoom_win32(kill_hidden)
        else:
            self._kill_zoom_darwin(kill_hidden)

    # pylint: disable=attribute-defined-outside-init
    def run(self, kill_hidden=False):
        '''
        Run the launch. kill_hidden==True quits hidden Zoom conf before launching.\n
        kill_hidden==False quits Zoom at the end of session and sends email
        '''
        self.kill_zoom(kill_hidden)

        # checker bool to send email
        self.is_send = not kill_hidden
    # pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    QuitZoom().run()

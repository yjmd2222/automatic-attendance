'''
Quit Zoom
'''

import pywinauto
from pywinauto.findwindows import ElementNotFoundError

from fake_attendance.abc import BaseClass
from fake_attendance.helper import print_with_time
from fake_attendance.notify import PrepareSendEmail
from fake_attendance.settings import ZOOM_CLASSROOM_CLASS

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

    def connect_and_kill(self, kill_hidden):
        'connect to Zoom conference and kill'
        try:
            pywinauto.Application().connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)\
                .kill(soft=True)
            if kill_hidden:
                print_with_time('숨겨진 Zoom 회의 종료')
            else:
                print_with_time('Zoom 회의 입장 확인 후 종료')
            if not self.result_dict['quit']['content']:
                self.result_dict['quit']['content'] = True
            return True
        except ElementNotFoundError:
            if kill_hidden:
                print_with_time('숨겨진 Zoom 회의 없음')
            else:
                print_with_time('Zoom 회의 입장 안 함')
            if self.result_dict['quit']['content'] is None:
                self.result_dict['quit']['content'] = False
            return False

    # pylint: disable=attribute-defined-outside-init
    def run(self, kill_hidden=False):
        '''
        Run the launch. kill_hidden==True quits hidden Zoom conf before launching.\n
        kill_hidden==False quits Zoom at the end of session and sends email
        '''
        # try killing Zoom completely in three tries
        for _ in range(3):
            if not self.connect_and_kill(kill_hidden):
                break

        # checker bool to send email
        self.is_send = not kill_hidden
    # pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    QuitZoom().run()

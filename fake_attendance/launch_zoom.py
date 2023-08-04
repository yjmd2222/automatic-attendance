'''
Launch Zoom
'''

import os
import sys

from sys import platform

import time

import keyboard

if platform == 'win32':
    import win32gui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.abc import UseSelenium
from fake_attendance.info import ZOOM_LINK
from fake_attendance.helper import (
    bring_chrome_to_front,
    print_with_time,
    set_foreground)
if platform == 'win32':
    from fake_attendance.helper import (
        print_all_windows,
        send_alt_key_and_set_foreground)
from fake_attendance.quit_zoom import QuitZoom
from fake_attendance.notify import PrepareSendEmail
from fake_attendance.settings import (
    ZOOM_AGREE_RECORDING_POPUP_CLASS,
    ZOOM_AGREE_RECORDING_POPUP_NAME,
    ZOOM_UPDATE_POPUP_CLASS,
    ZOOM_UPDATE_DOWNLOAD_CLASS,
    ZOOM_UPDATE_ACTUAL_UPDATE_CLASS,
    ZOOM_APPLICATION_NAME,
    ZOOM_CLASSROOM_NAME
    )
if platform == 'win32':
    from fake_attendance.settings import ZOOM_CLASSROOM_CLASS
# elif platform == 'darwin':
#     from fake_attendance.settings import (
#         ZOOM_APPLICATION_NAME,
#         ZOOM_CLASSROOM_NAME)
# pylint: enable=wrong-import-position

class LaunchZoom(PrepareSendEmail, UseSelenium):
    'A class for launching Zoom'
    print_name = '줌 실행'

    def __init__(self):
        'initialize'
        self.hwnd_zoom_classroom = 0
        PrepareSendEmail.define_attributes(self)
        PrepareSendEmail.decorate_run(self)
        UseSelenium.__init__(self)

    def reset_attributes(self):
        'reset attributes for next run'
        self.hwnd_zoom_classroom = 0
        PrepareSendEmail.define_attributes(self)

    def quit_zoom(self):
        'quit hidden Zoom windows if any'
        quit_zoom = QuitZoom()
        for _ in range(3):
            # if nothing to quit
            if not quit_zoom.run(kill_hidden=True):
                break
            # if something quit, wait for quitting to finish
            time.sleep(10)

    def connect(self):
        'connect to Zoom conference'
        # check presence of Zoom conference
        is_window, self.hwnd_zoom_classroom = self.check_window()
        # if visible
        if is_window:
            set_foreground(self.hwnd_zoom_classroom, ZOOM_APPLICATION_NAME, ZOOM_CLASSROOM_NAME)
            print_with_time('줌 회의 입장 확인')
        # if not visible
        else:
            print_with_time('줌 입장 안 함. 입장 실행')
            self.launch_zoom()

    def launch_zoom(self):
        'launch method'
        # initialize driver
        self.driver = self.initialize_selenium()

        # launch Zoom link
        print_with_time('줌 입장 시작')
        self.driver.get(ZOOM_LINK)
        # maximize and wait
        self.driver.maximize_window()
        time.sleep(5)

        # hack to focus on top
        # because recent Chrome does not allow bypassing this popup
        bring_chrome_to_front(self.driver)
        # click 'open Zoom in app'
        self.press_tabs_and_space(tab_num=2, reverse=False, send_alt=False)

        # quit driver for multiple tries
        self.driver.quit()
        self.driver = None

    def check_window_down(self, window_class=None, window_title=None):
        'wait until window is down'
        if window_class:
            hwnd = win32gui.FindWindow(window_class, None)
            window_name = window_class
        else:
            hwnd = win32gui.FindWindow(None, window_title)
            window_name = window_title
        # wait while it is visible
        while win32gui.IsWindowVisible(hwnd):
            print_with_time(f'{window_name} 진행중')
            time.sleep(5)

    def check_launch_result(self):
        'check the result'
        # check Zoom classroom
        is_classroom, self.hwnd_zoom_classroom = self.check_window()

        if is_classroom:
            self.result_dict[ZOOM_CLASSROOM_CLASS]['content'] = True
            return True
        # if not
        for _ in range(3):
            print_with_time('줌 회의 실행/발견 실패. 업데이트 중인지 확인 후 재실행')
            # check update
            self.process_popup(ZOOM_UPDATE_POPUP_CLASS, reverse=True, send_alt=True)
            # if agreed to update
            if self.result_dict[ZOOM_UPDATE_POPUP_CLASS]['content']:
                # downloading updates
                self.check_window_down(window_class=ZOOM_UPDATE_DOWNLOAD_CLASS)
                print_all_windows() # debug
                # updating Zoom
                self.check_window_down(window_class=ZOOM_UPDATE_ACTUAL_UPDATE_CLASS)
                print_all_windows() # debug
            self.launch_zoom()
            # check if now zoom window is visible
            is_classroom, self.hwnd_zoom_classroom = self.check_window()
            if is_classroom:
                return True

        # no launch from all tries
        print_with_time('줌 회의 실행/발견 모두 실패')
        return False

    def press_tabs_and_space(self, tab_num, reverse, send_alt):
        'press tabs and space in popup'
        # send alt because first key sent may be ignored
        if send_alt:
            keyboard.press_and_release('alt')
            time.sleep(0.1)
        hotkey = 'shift+tab' if reverse else 'tab'
        for _ in range(tab_num):
            keyboard.press_and_release(hotkey)
            time.sleep(0.1)
        keyboard.press_and_release('space')
        time.sleep(10)

    # pylint: disable=too-many-arguments
    def process_popup(self, window_class=None, window_title=None,\
                      tab_num=2, reverse=False, send_alt=False):
        'enter the popup'
        window_name = '' # will print this name
        try:
            assert not window_class == window_title == None,\
                'window_class와 window_title 둘 다 None일 수 없음'
        except AssertionError as error:
            print_with_time(f'입력 오류: {error}')
            return False
        # get hwnd
        if platform == 'win32':
            is_window, hwnd = self.check_window_win32(window_class)
            window_name = window_class
        elif platform == 'darwin':
            is_window, hwnd = self.check_window_darwin(ZOOM_APPLICATION_NAME, window_title)
            window_name = window_title
        # window/popup visible
        if is_window:
            print_with_time(f'{window_name} 창 확인')
            # set focus on it
            set_foreground(hwnd, ZOOM_APPLICATION_NAME, window_title)
            # press tab num times and hit space to enter
            self.press_tabs_and_space(tab_num, reverse, send_alt)
            self.result_dict[window_name]['content'] = True
        # agree window not visible
        else:
            if self.result_dict[window_name]['content']:
                print_with_time(f'{window_name} 동의 완료')
            else:
                print_with_time(f'{window_name} 동의 실패')
                self.result_dict[window_name]['content'] = False
        return self.result_dict[window_name]['content']
    # pylint: enable=too-many-arguments

    # pylint: disable=attribute-defined-outside-init
    def run(self):
        'Run the launch'
        self.quit_zoom() # kill hidden Zoom conference windows if any
        self.connect() # check connection. launch Zoom to connect if False
        # if launch successful
        if self.check_launch_result():
            # double check recording consent
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS, ZOOM_AGREE_RECORDING_POPUP_NAME, reverse=True, send_alt=True)
            print_with_time('동의 재확인')
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS, ZOOM_AGREE_RECORDING_POPUP_NAME, reverse=True, send_alt=True)
        # maximize if everything done correctly
        if self.result_dict[ZOOM_AGREE_RECORDING_POPUP_CLASS]['content']:
            self.maximize_window(self.hwnd_zoom_classroom)
        # chekcer bool to send email. See PrepareSendEmail.decorator_send_email_reset()
        self.is_send = True
    # pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    LaunchZoom().run()

'''
Launch Zoom
'''

import os
import sys

import time

import keyboard
import win32gui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.abc import UseSelenium
from fake_attendance.info import ZOOM_LINK
from fake_attendance.helper import (
    bring_chrome_to_front,
    print_with_time,
    print_all_windows,
    send_alt_key_and_set_foreground)
from fake_attendance.quit_zoom import QuitZoom
from fake_attendance.notify import Notify
from fake_attendance.settings import (
    ZOOM_AGREE_RECORDING_POPUP_CLASS,
    ZOOM_CLASSROOM_CLASS,
    ZOOM_UPDATE_POPUP_CLASS,
    ZOOM_UPDATE_DOWNLOAD_CLASS,
    ZOOM_UPDATE_ACTUAL_UPDATE_CLASS)
# pylint: enable=wrong-import-position

class LaunchZoom(UseSelenium):
    'A class for launching Zoom'

    def __init__(self):
        'initialize'
        self.hwnd_zoom_classroom = 0
        self.is_success = {
            ZOOM_UPDATE_POPUP_CLASS: {
                'name': '줌 업데이트',
                'result': False},
            ZOOM_CLASSROOM_CLASS:{
                'name': '줌 회의',
                'result': False
            },
            ZOOM_AGREE_RECORDING_POPUP_CLASS: {
                'name': '줌 녹화 동의',
                'result': False}
        }
        self.notify = Notify()
        self.print_name = '줌 실행'
        super().__init__()

    def reset_attributes(self):
        'reset attributes for next run'
        self.hwnd_zoom_classroom = 0
        self.is_success = {
            ZOOM_UPDATE_POPUP_CLASS: {
                'name': '줌 업데이트',
                'result': False},
            ZOOM_CLASSROOM_CLASS:{
                'name': '줌 회의',
                'result': False
            },
            ZOOM_AGREE_RECORDING_POPUP_CLASS: {
                'name': '줌 녹화 동의',
                'result': False}
        }
        self.notify = Notify()

    def quit_zoom(self):
        'quit hidden Zoom windows if any'
        quit_zoom = QuitZoom()
        for _ in range(3):
            # if nothing to quit
            if not quit_zoom.run(kill_hidden=True):
                break
            # if something quit, wait for quitting to finish
            time.sleep(10)

    def create_selenium_options(self):
        'not implemented'
        return None

    def connect(self):
        'connect to Zoom conference'
        # check presence of Zoom conference
        self.hwnd_zoom_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
        # if visible
        if win32gui.IsWindowVisible(self.hwnd_zoom_classroom):
            send_alt_key_and_set_foreground(self.hwnd_zoom_classroom)
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
        self.hwnd_zoom_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)

        def check_zoom_visible(hwnd):
            'check if zoom classroom window is visible'
            # if Zoom classroom visible
            if win32gui.IsWindowVisible(hwnd):
                print_with_time('줌 회의 실행/발견 성공')
                return True
            return False

        if check_zoom_visible(self.hwnd_zoom_classroom):
            return True
        # if not
        for _ in range(3):
            print_with_time('줌 회의 실행/발견 실패. 업데이트 중인지 확인 후 재실행')
            # check update
            self.process_popup(ZOOM_UPDATE_POPUP_CLASS, reverse=True, send_alt=True)
            # if agreed to update
            if self.is_success[ZOOM_UPDATE_POPUP_CLASS]['result']:
                # downloading updates
                self.check_window_down(window_class=ZOOM_UPDATE_DOWNLOAD_CLASS)
                print_all_windows() # debug
                # updating Zoom
                self.check_window_down(window_class=ZOOM_UPDATE_ACTUAL_UPDATE_CLASS)
                print_all_windows() # debug
            self.launch_zoom()
            # check if now zoom window is visible
            self.hwnd_zoom_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
            if check_zoom_visible(self.hwnd_zoom_classroom):
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
        if window_class:
            hwnd = win32gui.FindWindow(window_class, None)
            window_name = window_class
        else:
            hwnd = win32gui.FindWindow(None, window_title)
            window_name = window_title
        # window/popup visible
        if win32gui.IsWindowVisible(hwnd):
            print_with_time(f'{window_name} 창 확인')
            # set focus on it
            send_alt_key_and_set_foreground(hwnd)
            # press tab num times and hit space to enter
            self.press_tabs_and_space(tab_num, reverse, send_alt)
            self.is_success[window_name]['result'] = True
        # agree window not visible
        else:
            if self.is_success[window_name]['result']:
                print_with_time(f'{window_name} 동의 완료')
            else:
                print_with_time(f'{window_name} 동의 실패')
                self.is_success[window_name]['result'] = False
        return self.is_success[window_name]['result']
    # pylint: enable=too-many-arguments

    def run(self):
        'Run the launch'
        self.quit_zoom() # kill hidden Zoom conference windows if any
        self.connect() # check connection. launch Zoom to connect if False
        # if launch successful
        if self.check_launch_result():
            # double check recording consent
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS, reverse=True, send_alt=True)
            print_with_time('동의 재확인')
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS, reverse=True, send_alt=True)
        # send email
        self.notify.record_launch_result(self.is_success)
        self.notify.write_body_launch()
        self.notify.run()
        # maximize if everything done correctly
        if self.is_success[ZOOM_AGREE_RECORDING_POPUP_CLASS]['result']:
            self.maximize_window(self.hwnd_zoom_classroom)
        # reset attributes for next run
        self.reset_attributes()

if __name__ == '__main__':
    LaunchZoom().run()

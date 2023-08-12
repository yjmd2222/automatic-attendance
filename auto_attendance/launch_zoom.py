'''
Launch Zoom
'''

from sys import platform

import time

from selenium.webdriver.common.by import By
from pynput.keyboard import Key, Controller

from auto_attendance.abc import UseSelenium, ManipulateWindow
from auto_attendance.info import ZOOM_LINK
from auto_attendance.helper import (
    bring_chrome_to_front,
    get_last_image_match,
    print_with_time)
from auto_attendance.quit_zoom import QuitZoom
from auto_attendance.notify import PrepareSendEmail
from auto_attendance.settings import (
    ZOOM_AGREE_RECORDING_POPUP_CLASS,
    ZOOM_AGREE_RECORDING_POPUP_NAME, # they
    ZOOM_UPDATE_POPUP_CLASS,
    ZOOM_UPDATE_POPUP_NAME, # are
    ZOOM_UPDATE_DOWNLOAD_CLASS,
    ZOOM_UPDATE_DOWNLOAD_NAME, # missing
    ZOOM_UPDATE_ACTUAL_UPDATE_CLASS,
    ZOOM_UPDATE_ACTUAL_UPDATE_NAME, # values
    ZOOM_CLASSROOM_CLASS,
    ZOOM_CLASSROOM_NAME,
    LAUNCH_ZOOM_KEY_MAPPER,
    TAB_COUNT_MAPPER)
if platform == 'darwin':
    from auto_attendance.settings import (
        WINDOW_CHECK_IMAGE_MAPPER,
        OK_BUTTON_IMAGE_MAPPER)

    import pyautogui

class LaunchZoom(PrepareSendEmail, UseSelenium, ManipulateWindow):
    'A class for launching Zoom'
    print_name = '줌 실행'

    def __init__(self):
        'initialize'
        self.hwnd_zoom_classroom = 0
        self.keyboard = Controller()
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
        is_window, self.hwnd_zoom_classroom =\
            self.check_window(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_NAME)
        # if visible
        if is_window:
            self.set_foreground(self.hwnd_zoom_classroom)
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

        # click 회의 시작
        self.driver.find_element(By.XPATH, r'//*[text()="회의 시작"]').click()
        time.sleep(1)

        # click 'open Zoom in app'
        self.press_tabs_and_space(tab_num=TAB_COUNT_MAPPER['open_in_zoom'],
                                  reverse=False,
                                  send_alt=False)
        time.sleep(10)

        # quit driver for multiple tries
        self.driver.quit()
        self.driver = None

    def _check_window_down_win32(self, window_class, window_title):
        '''
        wait until window is down\n
        This should replace self.check_window_down()\n
        once Zoom properly adds support for AppleScript'''
        # pick os-dependent window name
        window = self.pick_os_dep_window_name(window_class, window_title)
        popup_name = LAUNCH_ZOOM_KEY_MAPPER[window]

        # wait while it is visible
        while self.check_window(window_class, window_title)[0]:
            print_with_time(f'{popup_name} 진행중')
            time.sleep(5)

    def _check_window_down_darwin(self, window_title):
        '''
        wait until window is down\n
        will be deprecated once Zoom properly adds support for AppleScript
        '''
        # get relevant image path
        window_check_image = WINDOW_CHECK_IMAGE_MAPPER[window_title]

        # will print this name
        popup_name = LAUNCH_ZOOM_KEY_MAPPER[window_title]

        # wait while it is visible
        while get_last_image_match(window_check_image) != (0.0, 0.0):
            print_with_time(f'{popup_name} 진행중')
            time.sleep(5)

    def check_window_down(self, window_class, window_title):
        '''
        wait until window is down
        '''
        if platform == 'win32':
            self._check_window_down_win32(window_class, window_title)
        else:
            self._check_window_down_darwin(window_title)

    def check_launch_result(self):
        'check the result'
        # check Zoom classroom
        is_classroom, self.hwnd_zoom_classroom =\
            self.check_window(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_NAME)

        # pick os-dependent name and find key for self.result_dict
        classroom = self.pick_os_dep_window_name(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_NAME)
        key = LAUNCH_ZOOM_KEY_MAPPER[classroom]

        if is_classroom:
            # either is fine for now
            print_with_time('줌 회의 실행/발견 성공')
            self.result_dict[key]['content'] = True
            return True
        # if not
        for _ in range(3):
            print_with_time('줌 회의 실행/발견 실패. 업데이트 중인지 확인 후 재실행')
            # check update
            self.process_popup(ZOOM_UPDATE_POPUP_CLASS,
                                ZOOM_UPDATE_POPUP_NAME,
                                tab_num=TAB_COUNT_MAPPER[self.pick_os_dep_window_name(
                                                            ZOOM_UPDATE_POPUP_CLASS,
                                                            ZOOM_UPDATE_POPUP_NAME)],
                                reverse=True,
                                send_alt=True)
            # if agreed to update
            if self.result_dict['줌 업데이트']['content']:
                # downloading updates
                self.check_window_down(ZOOM_UPDATE_DOWNLOAD_CLASS,
                                        ZOOM_UPDATE_DOWNLOAD_NAME)
                self.print_all_windows() # debug
                # updating Zoom
                self.check_window_down(ZOOM_UPDATE_ACTUAL_UPDATE_CLASS,
                                        ZOOM_UPDATE_ACTUAL_UPDATE_NAME)
                self.print_all_windows() # debug
            self.launch_zoom()
            # check if now zoom window is visible
            is_classroom, self.hwnd_zoom_classroom =\
                self.check_window(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_NAME)
            if is_classroom:
                print_with_time('줌 회의 실행/발견 성공')
                self.result_dict[classroom]['content'] = True
                return True

        # no launch from all tries
        print_with_time('줌 회의 실행/발견 모두 실패')
        return False

    def press_tabs_and_space(self, tab_num, reverse, send_alt):
        'press tabs and space in popup'
        # send alt because first key sent may be ignored
        if send_alt:
            self.keyboard.tap(Key.alt)
            time.sleep(0.1)

        keys = [Key.shift, Key.tab] if reverse else [Key.tab]

        def press_keys(keys:list):
            'press keys in sequence'
            keys_ = keys.copy()
            # base
            if not keys_:
                return
            # recursion
            current_key = keys_.pop(0)
            self.keyboard.press(current_key)
            press_keys(keys_)
            self.keyboard.release(current_key)
            return
        for _ in range(tab_num):
            press_keys(keys)
            time.sleep(0.1)
        self.keyboard.tap(Key.space)
        time.sleep(10)

    def pick_os_dep_window_name(self, window_class, window_title):
        'pick os-dependent window name from arguments'
        if platform == 'win32':
            window = window_class
        else:
            window = window_title

        return window

    # pylint: disable=too-many-arguments
    def process_popup(self, window_class, window_title,\
                        tab_num=2, reverse=False, send_alt=False):
        'hit OK on popup'
        if platform == 'win32':
            is_agreed = self._process_popup_win32(window_class, window_title,\
                        tab_num, reverse, send_alt)
        else:
            is_agreed = self._process_popup_darwin(window_title)

        return is_agreed

    def _process_popup_win32(self, window_class, window_title,\
                      tab_num=2, reverse=False, send_alt=False):
        '''
        hit OK on popup with keyboard on win32\n
        This should replace self.process_popup()\n
        once Zoom properly adds support for AppleScript
        '''
        # get os-dependent window name
        window = self.pick_os_dep_window_name(window_class, window_title)

        # get hwnd
        is_window, hwnd = self.check_window(window_class, window_title)

        # will print this name
        popup_name = LAUNCH_ZOOM_KEY_MAPPER[window]

        # window/popup visible
        if is_window:
            print_with_time(f'{popup_name} 창 확인')
            # set focus on it
            self.set_foreground(hwnd)
            # press tab num times and hit space to enter
            self.press_tabs_and_space(tab_num, reverse, send_alt)
            # store result
            self.result_dict[popup_name]['content'] = True
        # agree window not visible
        else:
            # already done
            if self.result_dict[popup_name]['content']:
                print_with_time(f'{popup_name} 동의 완료')
            # failed
            else:
                print_with_time(f'{popup_name} 동의 실패')
                self.result_dict[popup_name]['content'] = False
        return self.result_dict[popup_name]['content']
    # pylint: enable=too-many-arguments

    def _process_popup_darwin(self, window_title):
        '''
        click OK on popup on darwin\n
        will be deprecated once Zoom properly adds support for AppleScript
        '''
        # get relevant image paths
        window_check_image = WINDOW_CHECK_IMAGE_MAPPER[window_title]
        ok_button_image = OK_BUTTON_IMAGE_MAPPER[window_title]

        # will print this name
        popup_name = LAUNCH_ZOOM_KEY_MAPPER[window_title]

        # window/popup visible
        try:
            # checking popup itself
            window_check_pos = get_last_image_match(window_check_image)
            assert (window_check_image, window_check_pos) !=\
                (window_check_image, (0.0, 0.0))
            print_with_time(f'{popup_name} 창 확인')
            # checking ok button
            ok_button_pos = get_last_image_match(ok_button_image)
            assert (ok_button_image, ok_button_pos) !=\
                (ok_button_image, (0.0, 0.0))
            # click on ok button
            print(ok_button_image)
            pyautogui.click(ok_button_pos)
            # store result
            self.result_dict[popup_name]['content'] = True
        # agree window not visible
        except AssertionError as error:
            # already done
            if self.result_dict[popup_name]['content']:
                print_with_time(f'{popup_name} 동의 완료')
            # failed
            else:
                print_with_time(f'{popup_name} 동의 실패. 에러: {error}')
                self.result_dict[popup_name]['content'] = False
        return self.result_dict[popup_name]['content']

    # pylint: disable=attribute-defined-outside-init
    def run(self):
        'Run the launch'
        self.quit_zoom() # kill hidden Zoom conference windows if any
        self.connect() # check connection. launch Zoom to connect if False
        # if launch successful
        if self.check_launch_result():
            # double check recording consent
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS,
                                ZOOM_AGREE_RECORDING_POPUP_NAME,
                                tab_num=TAB_COUNT_MAPPER[self.pick_os_dep_window_name(
                                                         ZOOM_AGREE_RECORDING_POPUP_CLASS,
                                                         ZOOM_AGREE_RECORDING_POPUP_NAME)],
                                reverse=True,
                                send_alt=True)
            print_with_time('동의 재확인')
            # pyautogui confidence is low, so second time on mac may match '회의' in the menu bar
            self.process_popup(ZOOM_AGREE_RECORDING_POPUP_CLASS,
                                ZOOM_AGREE_RECORDING_POPUP_NAME,
                                tab_num=TAB_COUNT_MAPPER[self.pick_os_dep_window_name(
                                                         ZOOM_AGREE_RECORDING_POPUP_CLASS,
                                                         ZOOM_AGREE_RECORDING_POPUP_NAME)],
                                reverse=True,
                                send_alt=True)
        # maximize if everything done correctly
        if self.result_dict['줌 녹화 동의']['content']:
            self.maximize_window(self.hwnd_zoom_classroom)
        # checker bool to send email. See PrepareSendEmail.decorator_send_email_reset()
        self.is_send = True
    # pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    # pylint: disable=ungrouped-imports
    from auto_attendance.helper import fix_pyautogui
    fix_pyautogui()
    # pylint: enable=ungrouped-imports

    LaunchZoom().run()

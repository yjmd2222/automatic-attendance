'''
Launch Zoom
'''

import os
import sys

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import keyboard
import win32gui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.info import ZOOM_LINK
from fake_attendance.helper import print_with_time, send_alt_key_and_set_foreground
from fake_attendance.settings import (
    ZOOM_AGREE_RECORDING_POPUP_CLASS,
    ZOOM_CLASSROOM_CLASS,
    ZOOM_CLASSROOM_TITLE,
    ZOOM_LAUNCHING_CHROME_TITLE)
# pylint: enable=wrong-import-position

class LaunchZoom:
    'A class for launching Zoom'

    def __init__(self):
        'initialize'
        self.hwnd_zoom_classroom = 0
        self.hwnd_zoom_popup = 0
        self.hwnd_zoom_launching_chrome = 0
        self.driver = None
        self.is_running = False
        self.is_agreed = False

    def reset_attributes(self):
        'reset attributes for next run'
        self.hwnd_zoom_classroom = 0
        self.hwnd_zoom_popup = 0
        self.hwnd_zoom_launching_chrome = 0
        self.driver = None
        self.is_running = False
        self.is_agreed = False

    def connect(self):
        'connect to Zoom conference'
        # check presence of Zoom conference
        self.hwnd_zoom_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_TITLE)
        # if visible
        if win32gui.IsWindowVisible(self.hwnd_zoom_classroom):
            send_alt_key_and_set_foreground(self.hwnd_zoom_classroom)
            print_with_time('줌 회의 입장 확인')
            self.is_running = True
        # if not visible
        else:
            print_with_time('줌 입장 안 함. 실행 필요')
            self.is_running = False

    def initialize_selenium(self):
        'Initialize Selenium and return driver'
        auto_driver = Service(ChromeDriverManager().install())

        return webdriver.Chrome(service=auto_driver)

    def launch_zoom(self):
        'launch method'
        # driver init if Zoom shut down in middle
        if not self.driver:
            self.driver = self.initialize_selenium()

        # launch Zoom link
        print_with_time('줌 입장 시작')
        self.driver.get(ZOOM_LINK)
        self.driver.maximize_window()
        time.sleep(5)

        # connect to automated Chrome browser
        # because recent Chrome does not allow bypassing this popup
        self.hwnd_zoom_launching_chrome = win32gui.FindWindow(None, ZOOM_LAUNCHING_CHROME_TITLE)
        send_alt_key_and_set_foreground(self.hwnd_zoom_launching_chrome)

        # accept zoom launch message
        keyboard.press_and_release('tab')
        time.sleep(0.1)
        keyboard.press_and_release('tab')
        time.sleep(0.1)
        keyboard.press_and_release('space')
        time.sleep(10)

    def check_launch_result(self):
        'check the result'
        # check Zoom classroom
        self.hwnd_zoom_classroom = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, ZOOM_CLASSROOM_TITLE)
        # if Zoom classroom visible
        if win32gui.IsWindowVisible(self.hwnd_zoom_classroom):
            print_with_time('줌 회의 실행/발견 성공')
            return True
        # if not
        print_with_time('줌 회의 실행/발견 실패. 재실행')
        self.launch_zoom()
        return False

    def agree_recording(self):
        'agree recording'
        # hwnd of agree recording popup
        hwnd_zoom_popup = win32gui.FindWindow(ZOOM_AGREE_RECORDING_POPUP_CLASS, None)
        # agree window visible
        if win32gui.IsWindowVisible(hwnd_zoom_popup):
            # focus on the agree popup
            send_alt_key_and_set_foreground(hwnd_zoom_popup)
            # press tab 4 times and hit space to agree
            for _ in range(4):
                keyboard.press_and_release('tab')
                time.sleep(0.1)
            keyboard.press_and_release('space')
            self.is_agreed = True
        # agree window not visible
        else:
            if self.is_agreed:
                print_with_time('줌 녹화 동의 완료')
            else:
                print_with_time('줌 회의는 발견했지만 동의는 못 함')

    def run(self):
        'Run the launch'
        print_with_time('줌 실행 스크립트 시작')

        self.connect()

        if self.is_running:
            self.driver = self.initialize_selenium()
            self.launch_zoom()
        # check launch result and agree recording if success
        if self.check_launch_result():
            # double check
            self.agree_recording()
            time.sleep(5)
            print_with_time('동의 재확인')
            self.agree_recording()
        self.driver.quit()
        time.sleep(5)
        self.reset_attributes()

if __name__ == '__main__':
    LaunchZoom().run()

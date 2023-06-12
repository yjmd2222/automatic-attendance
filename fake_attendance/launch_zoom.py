'''
Launch Zoom
'''

import os
import sys

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pyautogui
import pywinauto
from pywinauto.findwindows import ElementNotFoundError

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.info import ZOOM_LINK
from fake_attendance.settings import (
    AGREE_RECORDING_IMAGE,
    ZOOM_AGREE_RECORDING_POPUP_CLASS,
    ZOOM_CLASSROOM_CLASS,
    ZOOM_LAUNCHING_CHROME)
from fake_attendance.helper import get_last_match
# pylint: enable=wrong-import-position

class LaunchZoom:
    'A class for launching Zoom'

    def __init__(self):
        'initialize'
        self.image = AGREE_RECORDING_IMAGE
        self.pywinauto_app = pywinauto.Application()
        self.driver = None

    def reset_attributes(self):
        'reset attributes for next run'
        self.pywinauto_app = pywinauto.Application()
        self.driver = None

    def connect(self):
        'connect to Zoom conference'
        # check presence of Zoom conference
        try:
            pywinauto.findwindows.find_element(class_name=ZOOM_CLASSROOM_CLASS)
            self.pywinauto_app.connect(class_name=ZOOM_CLASSROOM_CLASS, found_index=0)
            print('이미 줌 회의 입장중')
            # agree recording if there is popup
            self.agree_recording()
            return True
        # if there isn't
        except ElementNotFoundError:
            print('줌 입장 안 함. 실행 필요')
            return False

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
        self.driver.get(ZOOM_LINK)
        self.driver.maximize_window()
        time.sleep(5)

        # connect to automated Chrome browser
        # because recent Chrome does not allow bypassing this popup
        self.pywinauto_app.connect(title=ZOOM_LAUNCHING_CHROME).top_window().set_focus()

        # accept zoom launch message
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('space')
        time.sleep(10)

    def check_launch_result(self):
        'check the result'
        try:
            # Zoom's App class for conference.
            pywinauto.findwindows.find_element(class_name=ZOOM_CLASSROOM_CLASS)
            print('줌 회의 실행/발견 성공')
            return True
        except ElementNotFoundError:
            print('줌 회의 실행/발견 실패')
            self.launch_zoom()
            return False

    def agree_recording(self, trial=1):
        'agree recording'
        try:
            pywinauto.findwindows.find_element(class_name=ZOOM_AGREE_RECORDING_POPUP_CLASS)
            # focus on the agree popup
            self.pywinauto_app.connect(
                class_name=ZOOM_AGREE_RECORDING_POPUP_CLASS,
                found_index=0).top_window().set_focus()
            # find the agree button
            pos = get_last_match(self.image)
            # if agree button found
            if pos != (0,0,0,0):
                print('줌 녹화 동의 버튼 확인')
                pyautogui.click(pos)
                time.sleep(2)
            # if not found
            else:
                trial += 1
                print(f'중 녹화 동의 창 중에서 동의 버튼 확인 못 함.\
                      재시도 횟수: {trial}')
                # try again
                self.agree_recording(trial)
            # check if agree window is closed
            try:
                # if it is found
                pywinauto.findwindows.find_element(
                    class_name=ZOOM_AGREE_RECORDING_POPUP_CLASS)
                print(f'줌 녹화 동의 창 건재함. 재시도 횟수: {trial}')
                trial += 1
                # try again
                self.agree_recording(trial)
            # if it is not found
            except ElementNotFoundError:
                # successfully agreed
                print('줌 녹화 동의 완료')
                return
        # agree window not found
        except ElementNotFoundError:
            time.sleep(5)
            print(f'줌 녹화 동의 창 발견 실패, 재시도 횟수: {trial}')
            trial += 1
            # try again
            if not self.check_launch_result():
                print('줌 회의 중단됨')
                return
            self.agree_recording(trial)

    def run(self):
        'Run the launch'
        print('줌 실행 스크립트 시작')

        # if zoom already running, return
        if self.connect():
            self.reset_attributes()
            return

        # if not, launch Zoom
        self.driver = self.initialize_selenium()
        self.launch_zoom()
        # check launch result and agree recording if success
        if self.check_launch_result():
            self.agree_recording()
        self.driver.quit()
        time.sleep(5)
        self.reset_attributes()
        return

if __name__ == '__main__':
    LaunchZoom().run()

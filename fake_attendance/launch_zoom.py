'''
Launch Zoom
'''

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pyautogui
import pywinauto
from pywinauto.findwindows import ElementNotFoundError

from fake_attendance.info import ZOOM_LINK
from fake_attendance.settings import CONFERENCE_NAME

class LaunchZoom:
    'A class for launching Zoom'

    def __init__(self):
        'initialize'
        self.pywinauto_app = pywinauto.Application()

    def connect(self):
        'connect to Zoom conference'
        try:
            self.pywinauto_app.connect(title=CONFERENCE_NAME)
            print('이미 Zoom 회의 입장중')
            return True
        except ElementNotFoundError:
            print('Zoom 입장 안 함. 실행 필요')
            return False

    def initialize_selenium(self):
        'Initialize Selenium and return driver'
        auto_driver = Service(ChromeDriverManager().install())

        return webdriver.Chrome(service=auto_driver)

    def launch_zoom(self, driver):
        'launch method'
        driver.get(ZOOM_LINK)
        driver.maximize_window()
        time.sleep(5)

        # accept zoom launch message
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('space')
        time.sleep(10)

    def check_result(self):
        'check the result'
        try:
            self.pywinauto_app.connect(best_match=CONFERENCE_NAME)
            print('줌 실행 성공')
        except Exception as exc:
            print('줌 실행 실패')
            raise AssertionError from exc

    def run(self):
        'Run the launch'
        print('줌 실행 스크립트 시작')

        if self.connect():
            return

        driver = self.initialize_selenium()
        self.launch_zoom(driver)
        self.check_result()
        driver.quit()
        time.sleep(5)
        return

'''
Download Screen QR Reader source code
'''

import os
import sys

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import pyautogui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import get_last_match
from fake_attendance.settings import (CONTINUE_IMAGE, GET_CRX_LINK,
                  SCREEN_QR_READER_SOURCE, SCREEN_QR_READER_WEBSTORE_LINK)
# pylint: enable=wrong-import-position

class DownloadExtensionSource:
    'A class for downloading the source of Screen QR Reader'

    def __init__(self):
        'initialize'
        self.image = CONTINUE_IMAGE

    def check_source_exists(self):
        'Check if source exists'
        return os.path.isfile(SCREEN_QR_READER_SOURCE)

    def create_selenium_options(self):
        '''
        declare options for Selenium driver.
        Currently bypassing download warning seems impossible,
        so bypass options are not used.
        '''
        options = Options()
        options.add_experimental_option('prefs', {
          "download.default_directory": os.getcwd(),
          "download.prompt_for_download": False,
          "download.directory_upgrade": True
          })

        return options

    def initialize_selenium(self, options):
        'Initialize Selenium and return driver'
        auto_driver = Service(ChromeDriverManager().install())

        return webdriver.Chrome(service=auto_driver, options=options)

    def download(self, driver):
        'Download the source'
        driver.get(GET_CRX_LINK)
        driver.maximize_window()
        time.sleep(5)

        input_box = driver.find_element(By.ID, 'extension-url')
        input_box.send_keys(SCREEN_QR_READER_WEBSTORE_LINK)
        time.sleep(1)

        button_ok = driver.find_element(By.ID, 'form-extension-downloader-btn')
        button_ok.click()
        time.sleep(1)

        # Recent Chrome does not allow bypassing 'harmful download', so use pyautogui.
        pos = get_last_match(self.image)
        if pos != (0,0,0,0):
            print('다운로드 "계속" 버튼 확인')
            pyautogui.click(pos) # must be on the bottom
            time.sleep(5)
        else:
            print('다운로드 "계속" 버튼 찾을 수 없음')

    def run(self):
        'Run the download'
        print('다운로드 스크립트 실행')
        if self.check_source_exists():
            print('이미 디렉터리 안에 확장자 소스 파일 있음')
            return
        options = self.create_selenium_options()
        driver = self.initialize_selenium(options)
        self.download(driver)
        driver.quit()
        if os.path.isfile(SCREEN_QR_READER_SOURCE):
            print('다운로드한 확장자 소스 파일 확인 완료')
        else:
            print('다운로드된 파일 없음')
            raise AssertionError
        print('다운로드 스크립트 종료')
        return

if __name__ == '__main__':
    DownloadExtensionSource().run()

'''
Download Screen QR Reader source code
'''

import os
import sys

import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pyautogui

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.abc import UseSelenium
from fake_attendance.helper import (
    get_last_match,
    print_with_time)
from fake_attendance.settings import (
    CONTINUE_IMAGE,
    GET_CRX_LINK,
    SCREEN_QR_READER_SOURCE,
    SCREEN_QR_READER_WEBSTORE_LINK)
# pylint: enable=wrong-import-position

class DownloadExtensionSource(UseSelenium):
    'A class for downloading the source of Screen QR Reader'

    def __init__(self):
        'initialize'
        self.image = CONTINUE_IMAGE
        self.print_name = '다운로드'
        super().__init__()

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
            print_with_time('다운로드 "계속" 버튼 확인')
            pyautogui.click(pos) # must be on the bottom
            time.sleep(5)
        else:
            print_with_time('다운로드 "계속" 버튼 찾을 수 없음')

    def maximize_window(self, hwnd):
        print_with_time(f'maximize_window 하위클래스 {self.print_name}에서 사용 안 함')

    def run(self):
        'Run the download'
        if self.check_source_exists():
            print_with_time('이미 디렉터리 안에 확장자 소스 파일 있음')
            return
        options = self.create_selenium_options()
        driver = self.initialize_selenium(options)
        self.download(driver)
        driver.quit()
        if os.path.isfile(SCREEN_QR_READER_SOURCE):
            print_with_time('다운로드한 확장자 소스 파일 확인 완료')
        else:
            print_with_time('다운로드된 파일 없음. 모듈 종료')
            sys.exit()
        return

if __name__ == '__main__':
    DownloadExtensionSource().run()

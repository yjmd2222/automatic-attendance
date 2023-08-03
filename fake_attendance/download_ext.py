'''
Download Screen QR Reader source code
'''

import os
import sys

import time

from selenium.webdriver.common.by import By

import pyautogui

from fake_attendance.abc import UseSelenium
from fake_attendance.helper import (
    bring_chrome_to_front,
    get_file_path,
    get_last_match,
    print_with_time)
from fake_attendance.scheduler import MyScheduler
from fake_attendance.settings import (
    CONTINUE_IMAGE,
    GET_CRX_LINK,
    SCREEN_QR_READER_SOURCE,
    SCREEN_QR_READER_WEBSTORE_LINK)

class DownloadExtensionSource(UseSelenium):
    'A class for downloading the source of Screen QR Reader'
    print_name = '다운로드'

    def __init__(self, scheduler:MyScheduler|None=None):
        'initialize'
        self.image = CONTINUE_IMAGE
        self.scheduler = scheduler
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
        options = super().create_selenium_options()
        options.add_experimental_option('prefs', {
          "download.default_directory": os.getcwd(),
          "download.prompt_for_download": False,
          "download.directory_upgrade": True
          })

        return options

    def download(self):
        'Download the source'
        self.driver.get(GET_CRX_LINK)
        self.driver.maximize_window()
        time.sleep(5)

        input_box = self.driver.find_element(By.ID, 'extension-url')
        input_box.send_keys(SCREEN_QR_READER_WEBSTORE_LINK)
        time.sleep(1)

        button_ok = self.driver.find_element(By.ID, 'form-extension-downloader-btn')
        button_ok.click()
        time.sleep(1)

        # bring to front with hack
        bring_chrome_to_front(self.driver)

        # Recent Chrome does not allow bypassing 'harmful download', so use pyautogui.
        pos = get_last_match(self.image)
        if pos != (0,0,0,0):
            print_with_time('다운로드 "계속" 버튼 확인')
            pyautogui.click(pos) # must be on the bottom
            time.sleep(5)
        else:
            print_with_time('다운로드 "계속" 버튼 찾을 수 없음')

    def maximize_window(self, hwnd):
        'not implemented'
        return None

    def run(self):
        'Run the download'
        # quit if source already exists
        if self.check_source_exists():
            print_with_time('이미 디렉터리 안에 확장자 소스 파일 있음')
            return

        # init selenium
        self.driver = self.initialize_selenium()

        # track current directory list
        cur_listdir = os.listdir()

        # run the download
        self.download()

        # quit selenium
        self.driver.quit()

        # new directory list
        new_listdir = os.listdir()

        # check file download, exact match
        if os.path.isfile(SCREEN_QR_READER_SOURCE):
            print_with_time('다운로드한 확장자 소스 파일 확인 완료')
        else:
            # check if a .crx file was downloaded
            downloaded_file = [i for i in new_listdir if i not in cur_listdir][0]
            if '.crx' in downloaded_file:
                print_with_time(f'다운로드 파일 이름 일치 안 함: {downloaded_file}. 주의 필요')
                if self.scheduler:
                    # update source path
                    self.scheduler.fake_check_in.extension_source = get_file_path(downloaded_file)
            # if not
            else:
                print_with_time('다운로드된 확장자 소스 파일 없음. 모듈 종료')
                # quit everything because nothing will work
                sys.exit()
        return

if __name__ == '__main__':
    DownloadExtensionSource().run()

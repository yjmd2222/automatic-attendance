'''
Download Screen QR Reader source code
'''

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pyautogui

from info import (GET_CRX_LINK, IMAGE_CONTINUE, REGION,
                  SCREEN_QR_READER_SOURCE, SCREEN_QR_READER_WEBSTORE_LINK)

class DownloadExtensionSource:
    'A class for downloading the source of Screen QR Reader'

    def __init__(self):
        'initialize'
        self.image = os.path.join(os.getcwd(), 'images', IMAGE_CONTINUE)

    def check_source_exists(self):
        'Check if source exists'
        return os.path.isfile(os.path.join(os.getcwd(), SCREEN_QR_READER_SOURCE))

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
        return webdriver.Chrome(options=options)

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

        # Recent Chrome does not allow bypassing 'harmful download'.
        pos = pyautogui.locateOnScreen(self.image, region=REGION, confidence=0.7)
        i = 0
        while i < 4:
            i += 1
            if pos:
                pyautogui.click(pos)
                time.sleep(1)
                break

    def run(self):
        'Run the download'
        if self.check_source_exists():
            return
        options = self.create_selenium_options()
        driver = self.initialize_selenium(options)
        self.download(driver)
        driver.quit()
        return

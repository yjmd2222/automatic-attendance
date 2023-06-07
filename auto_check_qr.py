'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import time

import win32con
import win32gui

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from info import ID, PASSWORD
from settings import (SCREEN_QR_READER_POPUP_LINK, SCREEN_QR_READER_SOURCE,
                      ZOOM_RESIZE_PARAMETERS_LIST)

def decorator_three_times(func):
    'decorator for checking link three times, with different Zoom window sizes'
    def wrapper(*args):
        'wrapper'
        i = 0
        result = None
        while i < 3:
            # replace last argument == window_size
            args = args[:2] + (ZOOM_RESIZE_PARAMETERS_LIST[i],)
            result = func(*args)
            if result:
                break
            i += 1
        return result
    return wrapper

class FakeCheckIn:
    'A class for checking QR image and sending email with link'

    def __init__(self):
        'initialize'
        self.options = self.create_selenium_options() # Selenium options
        self.zoom_window = win32gui.FindWindow(None, 'Zoom 회의')

    def create_selenium_options(self):
        'declare options for Selenium driver'
        options = Options()
        # Screen QR Reader source required
        options.add_extension(SCREEN_QR_READER_SOURCE)
        # automatically select Zoom meeting
        options.add_argument('--auto-select-desktop-capture-source=Zoom')

        return options

    def initialize_selenium(self):
        'initialize Selenium and return driver'
        return webdriver.Chrome(options=self.options)

    @decorator_three_times
    def get_link(self, driver, window_sizes):
        'Get link from QR'
        # maximize Chrome window
        driver.maximize_window()
        # reduce Zoom window size
        win32gui.MoveWindow(self.zoom_window, *window_sizes, True)
        driver.get(SCREEN_QR_READER_POPUP_LINK) # Screen QR Reader
        time.sleep(5)

        # Selenium will automatically open the link in a new tab
        # if there is a QR image, so check tab count.
        window_handles = driver.window_handles

        if len(window_handles) > 1:
            driver.switch_to.window(window_handles[1]) # force Selenium to be on the new tab
            return True

        return False

    def check_in(self, driver):
        'do the check-in'
        with_kakao = driver.find_element(By.CLASS_NAME, 'login-form__button-title.css-caslt6')
        with_kakao.click()
        time.sleep(3)

        id_box = driver.find_element(By.ID, 'loginKey--1')
        id_box.send_keys(ID)
        time.sleep(1)

        pw_box = driver.find_element(By.ID, 'password--2')
        pw_box.send_keys(PASSWORD)
        time.sleep(1)

        press_login = driver.find_element(By.CLASS_NAME, 'btn_g.highlight.submit')
        press_login.click()
        time.sleep(10)

        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        iframe_url = iframe.get_attribute('src')
        driver.get(iframe_url)
        time.sleep(10)

        agree_button = driver.find_element(By.XPATH, "//*[text()='동의합니다.']")
        agree_button.click()
        time.sleep(3)

        check_in_button = driver.find_element(By.XPATH, "//*[text()='출석']")
        check_in_button.click()
        time.sleep(3)

        submit_button = driver.find_element(By.XPATH, "//*[text()='제출']")
        submit_button.click()
        time.sleep(1)

    def run(self):
        'run once'
        driver = self.initialize_selenium()
        islink = self.get_link(driver)
        # if there's no link
        if not islink:
            print('QR 코드 없음. 현 세션 완료')
        # otherwise check in
        else:
            self.check_in(driver)
        driver.quit()
        # maximize Zoom window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_MAXIMIZE)
FakeCheckIn().run()
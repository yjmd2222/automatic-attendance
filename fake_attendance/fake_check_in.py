'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import os
import sys

from functools import wraps

import time

import win32con
import win32gui

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.info import KAKAO_ID, KAKAO_PASSWORD
from fake_attendance.helper import print_with_time
from fake_attendance.settings import (
    SCREEN_QR_READER_BLANK,
    SCREEN_QR_READER_POPUP_LINK,
    SCREEN_QR_READER_SOURCE,
    ZOOM_RESIZE_PARAMETERS_LIST,
    LOGIN_WITH_KAKAO_BUTTON,
    ID_INPUT_BOX,
    PASSWORD_INPUT_BOX,
    LOGIN_BUTTON,
    AGREE,
    CHECK_IN,
    SUBMIT)
from fake_attendance.notify import SendEmail
# pylint: enable=wrong-import-position

def decorator_repeat_diff_sizes(func):
    'decorator for checking link multiple times, with different Zoom window sizes'
    @wraps(func) # needed for wrapping class methods with *args
    def wrapper(self, *args):
        'wrapper'
        i = 0
        result = None
        while i < len(ZOOM_RESIZE_PARAMETERS_LIST):
            # replace last argument == ratio
            args = args[:-1] + (ZOOM_RESIZE_PARAMETERS_LIST[i],)
            result = func(self, *args)
            if result:
                break
            i += 1
        return result
    return wrapper

class FakeCheckIn:
    'A class for checking QR image and sending email with link'

    def __init__(self):
        'initialize'
        self.is_window = False
        self.zoom_window = 0
        self.rect = [100,100,100,100]
        self.is_wait = False
        self.send_email = SendEmail()

    def reset_attributes(self):
        'reset attributes for next run'
        self.is_window, self.zoom_window = self.check_window()
        self.rect = self.get_max_window_size() if self.is_window else []
        self.is_wait = False
        self.send_email = SendEmail()

    def check_window(self):
        'check and return window'
        window = win32gui.FindWindow(None, 'Zoom 회의')
        self.is_window = bool(window) # True if window not 0 else False

        return bool(window), window

    def get_max_window_size(self):
        'get max window size'
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_MAXIMIZE)

        return list(win32gui.GetWindowRect(self.zoom_window))

    @decorator_repeat_diff_sizes
    def get_link(self, driver, ratio):
        'Get link from QR'
        # maximize Chrome window
        driver.maximize_window()
        time.sleep(1)
        # calculate new window size
        rect_resized = self.rect.copy()
        for idx, _ in enumerate(self.rect[2:]):
            rect_resized[idx+2] = int(self.rect[idx+2]*ratio)
        # apply new window size
        win32gui.MoveWindow(self.zoom_window, *rect_resized, True)
        driver.get(SCREEN_QR_READER_POPUP_LINK) # Screen QR Reader
        time.sleep(2)

        # Selenium will automatically open the link in a new tab
        # if there is a QR image, so check tab count.
        window_handles = driver.window_handles

        # Screen QR Reader may open 'about:blank' when there is not a valid QR image.
        if len(window_handles) > 1: # if there are two tabs
            driver.switch_to.window(window_handles[-1]) # force Selenium to be on the new tab
            # check if the url is fake then return False
            if driver.current_url in (SCREEN_QR_READER_BLANK, SCREEN_QR_READER_POPUP_LINK):
                return False
            return True # return True if url is valid

        return False

    def create_selenium_options(self):
        'declare options for Selenium driver'
        options = Options()
        # Screen QR Reader source required
        options.add_extension(SCREEN_QR_READER_SOURCE)
        # automatically select Zoom meeting
        options.add_argument('--auto-select-desktop-capture-source=Zoom')

        return options

    def initialize_selenium(self, options):
        'initialize Selenium and return driver'
        auto_driver = Service(ChromeDriverManager().install())

        return webdriver.Chrome(service=auto_driver, options=options)

    def check_in(self, driver):
        'do the check-in'
        # login type
        with_kakao = driver.find_element(By.CLASS_NAME, LOGIN_WITH_KAKAO_BUTTON)
        with_kakao.click()
        time.sleep(10)

        # insert Kakao id
        id_box = driver.find_element(By.ID, ID_INPUT_BOX)
        id_box.send_keys(KAKAO_ID)
        time.sleep(1)

        # insert Kakao password
        pw_box = driver.find_element(By.ID, PASSWORD_INPUT_BOX)
        pw_box.send_keys(KAKAO_PASSWORD)
        time.sleep(1)

        # log in
        press_login = driver.find_element(By.CLASS_NAME, LOGIN_BUTTON)
        press_login.click()
        time.sleep(10)

        # Should have successfully logged in. Now pass link to SendEmail
        link = driver.current_url
        self.send_email.get_link(link)
        time.sleep(5)

        # get inner document link
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        iframe_url = iframe.get_attribute('src')
        driver.get(iframe_url)
        time.sleep(10)

        # agree to check in
        agree_button = driver.find_element(By.XPATH, AGREE)
        agree_button.click()
        time.sleep(3)

        # select check-in
        check_in_button = driver.find_element(By.XPATH, CHECK_IN)
        check_in_button.click()
        time.sleep(3)

        # submit
        submit_button = driver.find_element(By.XPATH, SUBMIT)
        try:
            driver.execute_script('arguments[0].click();', submit_button)
            self.send_email.get_result('성공')
            self.is_wait = True
        except ElementClickInterceptedException:
            self.send_email.get_result('실패')
            self.is_wait = False

    def run(self):
        'run once'
        self.is_window, self.zoom_window = self.check_window()
        self.rect = self.get_max_window_size()
        if self.is_window:
            options = self.create_selenium_options()
            driver = self.initialize_selenium(options)
        else:
            print_with_time('줌 실행중인지 확인 필요')
            self.reset_attributes()
            return
        is_link = self.get_link(driver, 0)
        # if there's no link
        if not is_link:
            print_with_time('QR 코드 없음. 현 세션 완료')
        # otherwise check in
        else:
            print_with_time('QR 코드 확인. 출석 체크 진행')
            self.check_in(driver)
            # send email
            self.send_email.send_email()
        driver.quit()
        # maximize Zoom window
        win32gui.MoveWindow(self.zoom_window, *self.rect, True)
        # make sure same job does not run within 15 minutes upon completion
        if self.is_wait:
            time.sleep(900)
        self.reset_attributes()
        return

if __name__ == '__main__':
    FakeCheckIn().run()

'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

from datetime import datetime, timedelta
import time

from pywintypes import error

import win32con
import win32gui

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from fake_attendance.info import ID, PASSWORD
from fake_attendance.settings import (
    MINUTES,
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

def decorator_four_times(func):
    'decorator for checking link four times, with different Zoom window sizes'
    def wrapper(*args):
        'wrapper'
        i = 0
        result = None
        while i < 4:
            # replace last argument == window_size
            args = args[:3] + (ZOOM_RESIZE_PARAMETERS_LIST[i],)
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
        self.zoom_window = win32gui.FindWindow(None, 'Zoom 회의')

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

    @decorator_four_times
    def get_link(self, driver, next_time_strf, window_sizes=(0, 0, 1914, 751)):
        'Get link from QR'
        # maximize Chrome window
        driver.maximize_window()
        time.sleep(1)
        # reduce Zoom window size
        try:
            win32gui.MoveWindow(self.zoom_window, *window_sizes, True)
        except error:
            print('줌 실행중인지 확인 필요')
            print('다음 출석 스크립트 실행 시각:', next_time_strf)
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
        with_kakao = driver.find_element(By.CLASS_NAME, LOGIN_WITH_KAKAO_BUTTON)
        with_kakao.click()
        time.sleep(10)

        id_box = driver.find_element(By.ID, ID_INPUT_BOX)
        id_box.send_keys(ID)
        time.sleep(1)

        pw_box = driver.find_element(By.ID, PASSWORD_INPUT_BOX)
        pw_box.send_keys(PASSWORD)
        time.sleep(1)

        press_login = driver.find_element(By.CLASS_NAME, LOGIN_BUTTON)
        press_login.click()
        time.sleep(10)

        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        iframe_url = iframe.get_attribute('src')
        driver.get(iframe_url)
        time.sleep(10)

        agree_button = driver.find_element(By.XPATH, AGREE)
        agree_button.click()
        time.sleep(3)

        check_in_button = driver.find_element(By.XPATH, CHECK_IN)
        check_in_button.click()
        time.sleep(3)

        submit_button = driver.find_element(By.XPATH, SUBMIT)
        # submit_button.click()
        # Element is not clickable at point (X,Y) error
        driver.execute_script('arguments[0].click();', submit_button)
        time.sleep(600) # to make sure same job does not run within 10 minutes

    def run(self):
        'run once'
        now = datetime.now()
        next_time = now + timedelta(minutes=MINUTES)
        next_time_strf = next_time.strftime("%H:%M:%S")
        options = self.create_selenium_options()
        driver = self.initialize_selenium(options)
        islink = self.get_link(driver, next_time_strf)
        # if there's no link
        if not islink:
            print('QR 코드 없음. 현 세션 완료')
        # otherwise check in
        else:
            self.check_in(driver)
        driver.quit()
        # maximize Zoom window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_MAXIMIZE)

        next_time = now + timedelta(minutes=MINUTES)
        print('다음 출석 스크립트 실행 시각:', next_time.strftime("%H:%M:%S"))

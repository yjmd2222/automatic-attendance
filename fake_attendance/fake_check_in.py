'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import os
import sys

from datetime import datetime, timedelta
import time

import win32con
import win32gui

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
    ZOOM_CLASSROOM_CLASS,
    LOGIN_WITH_KAKAO_BUTTON,
    ID_INPUT_BOX,
    PASSWORD_INPUT_BOX,
    LOGIN_BUTTON,
    IFRAME,
    AGREE,
    CHECK_IN,
    SUBMIT)
from fake_attendance.notify import SendEmail
# pylint: enable=wrong-import-position

class FakeCheckIn:
    'A class for checking QR image and sending email with link'

    def __init__(self):
        'initialize'
        self.is_window = False
        self.zoom_window = 0
        self.rect = [100,100,100,100]
        self.is_wait = False
        self.until = None
        self.send_email = SendEmail()

    def reset_attributes(self):
        'reset attributes for next run'
        self.is_window, self.zoom_window = self.check_window()
        self.rect = self.get_max_window_size() if self.is_window else []
        self.is_wait = False
        self.send_email = SendEmail()

    def check_window(self):
        'check and return window'
        window = win32gui.FindWindow(ZOOM_CLASSROOM_CLASS, None)
        self.is_window = bool(window) # True if window not 0 else False

        return bool(window), window

    def get_max_window_size(self):
        'get max window size'
        # force normal size from possible out-of-size maximized window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_NORMAL)
        # maximize window
        win32gui.ShowWindow(self.zoom_window, win32con.SW_MAXIMIZE)

        return list(win32gui.GetWindowRect(self.zoom_window))

    def check_link_loop(self, driver):
        'Get link from QR'
        # maximize Chrome window
        driver.maximize_window()
        time.sleep(1)

        # calculate new window size
        ratios = [i/10 for i in range(3, 11)]
        rect_resized = self.rect.copy()
        result = None
        # only horizontally
        for ratio in ratios:
            rect_resized[2] = int(self.rect[2] * ratio)
            result = self.check_link(driver, rect_resized)
            if result:
                break
        # both horizontally and vertically
        if not result:
            for ratio in ratios:
                rect_resized[2] = int(self.rect[2] * ratio)
                rect_resized[3] = int(self.rect[3] * ratio)
                result = self.check_link(driver, rect_resized)
                if result:
                    break

        return result

    def check_link(self, driver, rect_resized):
        'method to actually fire Screen QR Reader inside loop'
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

    def selenium_action(self, driver, by_which, sleep, **kwargs):
        '''
        selenium action method\n
        Must specify kwargs\n
        'how' must be one of 'click', 'input', 'get_iframe', and 'submit'\n
        'element' is the element to be inspected\n
        'input_text' must be given if 'how' is 'input'
        '''
        # check three times
        for _ in range(3):
            try:
                element = driver.find_element(by_which, kwargs['element'])
                if kwargs['how'] == 'click':
                    element.click()
                elif kwargs['how'] == 'input':
                    element.send_keys(kwargs['input_text'])
                elif kwargs['how'] == 'get_iframe':
                    iframe_url = element.get_attribute('src')
                    driver.get(iframe_url)
                elif kwargs['how'] == 'submit':
                    driver.execute_script('arguments[0].click();', element)
                else:
                    raise AssertionError
                print_with_time(f'{kwargs["element"]} 찾기 성공. {sleep}초 후 다음 단계로 진행')
                time.sleep(sleep)
                return True
            except NoSuchElementException:
                print_with_time(f'{kwargs["element"]} 찾기 실패. {sleep}초 후 재시도')
                time.sleep(sleep)

        print_with_time('재시도 전부 실패. 현 상태에서 이메일 발송')
        return False

    def check_in(self, driver):
        'do the check-in'
        # login type
        is_login_type = self.selenium_action(driver, By.CLASS_NAME, 10,\
                        how='click', element=LOGIN_WITH_KAKAO_BUTTON)

        # insert Kakao id
        is_id_box = None
        if is_login_type:
            is_id_box = self.selenium_action(driver, By.ID, 1,\
                                        how='input', element=ID_INPUT_BOX, input_text=KAKAO_ID)

        # insert Kakao password
        is_pw_box = None
        if is_id_box:
            is_pw_box = self.selenium_action(driver, By.ID, 1,\
                        how='input', element=PASSWORD_INPUT_BOX, input_text=KAKAO_PASSWORD)

        # log in
        is_press_login = None
        if is_pw_box:
            is_press_login = self.selenium_action(driver, By.CLASS_NAME, 10,\
                        how='click', element=LOGIN_BUTTON)

        # get inner document link
        is_iframe = None
        if is_press_login:
            # Should have successfully logged in. Now pass link to SendEmail
            link = driver.current_url
            self.send_email.record_link(link)
            time.sleep(5)
            is_iframe = self.selenium_action(driver, By.TAG_NAME, 10,\
                        how='get_iframe', element=IFRAME)

        # agree to check in
        is_agree = None
        if is_iframe:
            is_agree = self.selenium_action(driver, By.XPATH, 3,\
                        how='click', element=AGREE)

        # select check-in
        is_check_in = None
        if is_agree:
            is_check_in = self.selenium_action(driver, By.XPATH, 3,\
                        how='click', element=CHECK_IN)

        # submit
        is_submit = None
        if is_check_in:
            is_submit = self.selenium_action(driver, By.XPATH, 3,\
                        how='submit', element=SUBMIT)

        # send email
        if is_submit:
            self.send_email.record_result('성공')
            self.is_wait = True
        else:
            self.send_email.record_result('실패')
            self.is_wait = False

    def run(self):
        'run once'
        # make sure same job does not run within 30 minutes upon completion
        if self.until and datetime.now() < self.until: # self.until is set towards the end
            print_with_time(f'기존 출석 확인. {datetime.strftime(self.until, "%H:%M")}까지 출석 체크 실행 안 함')
            return
        self.is_window, self.zoom_window = self.check_window()
        self.rect = self.get_max_window_size()
        if self.is_window:
            options = self.create_selenium_options()
            driver = self.initialize_selenium(options)
        else:
            print_with_time('줌 실행중인지 확인 필요')
            self.reset_attributes()
            return
        is_link = self.check_link_loop(driver)
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
        # make sure same job does not run within 30 minutes upon completion
        if self.is_wait:
            self.until = datetime.now() + timedelta(minutes=30)
            print_with_time(f'출석 체크 완료. {datetime.strftime(self.until, "%H:%M")}까지 출석 체크 실행 안 함')
        else:
            print_with_time('QR 코드 확인 후 출석 체크 실패')
        self.reset_attributes()
        return

if __name__ == '__main__':
    FakeCheckIn().run()

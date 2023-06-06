'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import time

import smtplib
from email.mime.text import MIMEText

from datetime import datetime

from apscheduler.schedulers.background import BlockingScheduler

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from info import GMAIL_APP_PASSWORD, EMAIL_ADDRESS, SCREEN_QR_READER_POPUP_LINK, SCREEN_QR_READER_SOURCE, MINUTES

def decorator_three_times(func):
    'decorator for checking link three times'
    def wrapper(*args, **kwargs):
        'wrapper'
        i = 3
        result = None
        while i > 0:
            result = func(*args, **kwargs)
            if result:
                break
            i -= 1
        return result
    return wrapper

class FakeCheckIn:
    'A class for checking QR image and sending email with link'

    def __init__(self):
        'initialize'
        self.options = self.create_selenium_options() # Selenium options

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
    def get_link(self, driver):
        'Get link from QR'
        driver.maximize_window()
        driver.get(SCREEN_QR_READER_POPUP_LINK) # Screen QR Reader
        time.sleep(5)

        # Selenium will automatically open the link in a new tab
        # if there is a QR image, so check tab count.
        window_handles = driver.window_handles

        link = ''
        if len(window_handles) > 1:
            driver.switch_to.window(window_handles[1]) # force Selenium to be on the new tab
            link = driver.current_url

        return link

    def send_email(self, link):
        'send email with SMTP'
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, GMAIL_APP_PASSWORD)

        msg = MIMEText(link)
        msg['Subject'] = f'출석 링크 {datetime.now().strftime(r"%Y-%m-%d %H:%M")}'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print('이메일 발송 성공')

        smtp.quit()

    def run(self):
        'run once'
        driver = self.initialize_selenium()
        link = self.get_link(driver)
        # if self.link empty
        if not link:
            print('QR 코드 없음. 이메일 발송 안 함')
        # otherwise send email
        else:
            self.send_email(link)
        driver.quit()
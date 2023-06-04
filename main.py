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

from info import GMAIL_APP_PASSWORD, EMAIL_ADDRESS, CHROME_EXTENSION_LINK

class FakeCheckIn:
    'A class for checking QR image and sending email with link'

    def decorator_three_times(func:function):
        'decorator for checking link three times'
        def wrapper(self, *args, **kwargs):
            'wrapper'
            i = 3
            result = None
            while i > 0:
                result = func(self, *args, **kwargs)
                if result:
                    break
                i -= 1
            return result
        return wrapper

    def __init__(self):
        'initialize'
        self.driver = self.initialize_selenium()

    def initialize_selenium(self):
        'initialize selenium and return driver'
        options = Options()
        # Screen QR Reader source required
        options.add_extension('./extension_0_1_2_0.crx')
        # automatically select Zoom meeting
        options.add_argument('--auto-select-desktop-capture-source=Zoom')

        driver = webdriver.Chrome(options=options)

        return driver

    @decorator_three_times
    def get_link(self):
        'Get link from QR'
        self.driver.get(CHROME_EXTENSION_LINK) # Screen QR Reader
        time.sleep(5)

        # Selenium will automatically open the link in a new tab
        # if there is a QR image, so check tab count.
        window_handles = self.driver.window_handles

        link = ''
        if len(window_handles) > 1:
            self.driver.switch_to.window(window_handles[1]) # force Selenium to be on the new tab
            link = self.driver.current_url

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
        link = self.get_link()
        # if self.link empty
        if not link:
            print('QR 코드 없음. 이메일 발송 안 함')
        # otherwise send email
        else:
            self.send_email(link)
        self.driver.quit()

if __name__ == '__main__':
    sched = BlockingScheduler(standalone=True)          # scheduler
    program = FakeCheckIn()                             # app
    sched.add_job(program.run, 'interval', seconds=300) # will run app every 300 seconds

    try:
        sched.start()
    except KeyboardInterrupt as e:
        print('interrupted')

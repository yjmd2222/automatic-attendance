'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

import os
import time
from functools import partial

import smtplib
from email.mime.text import MIMEText

from datetime import datetime

from apscheduler.schedulers.background import BlockingScheduler

import pyautogui
import pywinauto
import pyperclip
from PIL import ImageGrab

from info import *

class FakeCheckIn:
    'A class for checking QR image and sending email with link'
    def __init__(self):
        'initialize'
        self.chrome_path = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Chrome.lnk'
        self.images_base_path = os.path.join(os.getcwd(), 'images')

        self.link = ''

        self.pywinauto_app = pywinauto.Application()

    def get_pos(self, image):
        'Gets position of image on screen'
        image_path = os.path.join(self.images_base_path, image+'.png')
        return pyautogui.locateCenterOnScreen(image_path, confidence=0.7)

    def copy_clipboard(self):
        'Copy highlighted text'
        pyautogui.hotkey('ctrl', 'a') # select all
        time.sleep(0.01)
        pyautogui.hotkey('ctrl', 'c') # copy
        time.sleep(0.01)
        return pyperclip.paste()

    def click_pos_and_sleep(self, pos:tuple):
        'make a click in given pos'
        print(pos)
        pyautogui.click(pos)
        time.sleep(1)

    def click_image_and_sleep(self, image, offset=None):
        'make a click on the given image. Calls click_pos_and_sleep'
        pos = self.get_pos(image)
        # apply offset
        if offset:
            pos = (pos[0] + offset[0], pos[1] + offset[1])
        print(image)
        self.click_pos_and_sleep(pos)

    def get_link(self):
        'method for getting link from Zoom'
        # bring zoom meeting to front to make sure the meeting is on the list
        self.pywinauto_app.connect(best_match='Zoom 회의').top_window().set_focus()

        # start chrome
        os.system('start "" "' + self.chrome_path)
        time.sleep(3)
        self.click_image_and_sleep('qr_extension_icon')
        self.click_image_and_sleep('qr_zoom')
        self.click_image_and_sleep('qr_share')

        # search bar
        if not self.get_pos('qr_fail_message'):
            # self.click_image_and_sleep('chrome_bfr_icons', (100, 0))
            self.link = self.copy_clipboard()

        # close chrome
        pyautogui.click() # ensure chrome is selected
        pyautogui.hotkey('alt', 'f4')
        time.sleep(0.01)

    def send_email(self):
        'send email with SMTP'
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, GMAIL_APP_PASSWORD)

        msg = MIMEText(self.link)
        msg['Subject'] = f'출석 링크 {datetime.now().strftime(r"%Y-%m-%d %H:%M")}'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print('이메일 발송 성공')

        smtp.quit()

    def run(self):
        'run once'
        self.get_link()
        # if self.link empty
        if not self.link:
            print('QR 코드 없음. 이메일 발송 안 함')
            return
        # otherwise send email
        self.send_email()
        return

if __name__ == '__main__':
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True) # multimonitor support

    sched = BlockingScheduler(standalone=True)          # scheduler
    program = FakeCheckIn()                               # app
    sched.add_job(program.run, 'interval', seconds=300) # will run app every 300 seconds

    try:
        sched.start()
    except KeyboardInterrupt as e:
        print('interrupted')

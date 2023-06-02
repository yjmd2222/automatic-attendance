import pyautogui
import pywinauto
import pyperclip
from PIL import ImageGrab
from functools import partial

import os
import time

import smtplib
from email.mime.text import MIMEText

from datetime import datetime

from info import *

class SendEmail:
    def __init__(self):
        self.chrome_path = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Chrome.lnk'
        self.images_base_path = os.path.join(os.getcwd(), 'images')

        self.link = ''

        self.pywinauto_app = pywinauto.Application()

    def get_pos(self, image):
        image_path = os.path.join(self.images_base_path, image+'.png')
        return pyautogui.locateCenterOnScreen(image_path, confidence=0.7)

    def copy_clipboard(self):
        'copy highlighted text'
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
        pos = self.get_pos(image)
        # apply offset
        if offset: pos = (pos[0] + offset[0], pos[1] + offset[1])
        print(image)
        self.click_pos_and_sleep(pos)

    def get_link(self):
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
        try: 
            while True:
                self.get_link()
                # if self.link empty
                if not self.link:
                    print('QR 코드 없음. 이메일 발송 안 함')
                    time.sleep(300) # 5분 wait
                    continue
                # otherwise send email
                self.send_email()
                time.sleep(300) # 5분 wait
        except KeyboardInterrupt:
            print('Interrupted')

if __name__ == '__main__':
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True) # multimonitor support
    program = SendEmail()
    program.run()
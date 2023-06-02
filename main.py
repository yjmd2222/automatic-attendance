import pyautogui
import pywinauto
import pyperclip

import os
import time

import smtplib
from email.mime.text import MIMEText

from datetime import datetime

from info import *

class SendEmail:
    def __init__(self):
        # where to click
        self.qr_extension_icon_pos = (1774, 56)         # qr reader icon extension
        self.qr_zoom_pos = (1379, 281)                  # zoom window from selection in qr reader
        self.qr_share_pos = (1565, 603)                 # share button on qr reader
        self.chrome_link_pos = (572, 46)                # search bar link in chrome
        self.chrome_exit_button_pos = (1898, 21)        # chrome exit button
        self.prefix_text = 'asdfkjnzxcvlkjnsadfkjljnjk' # a meaningless text so nothing matches if nothing in searchbar

        self.chrome_path = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Chrome.lnk'

        self.link = ''

        self.pywinauto_app = pywinauto.Application()

    def copy_clipboard(self):
        'copy highlighted text'
        pyautogui.hotkey('ctrl', 'a') # select all
        time.sleep(.01)
        pyautogui.hotkey('ctrl', 'c') # copy
        time.sleep(.01)
        return pyperclip.paste()

    def click_and_sleep(seflf, pos:tuple):
        'make a click in given pos'
        pyautogui.click(pos)
        time.sleep(1)

    def get_link(self):
        # bring zoom meeting to front.
        self.pywinauto_app.connect(best_match='Zoom 회의').top_window().set_focus()

        # start chrome
        os.system('start "" "' + self.chrome_path)
        time.sleep(3)
        self.click_and_sleep(self.qr_extension_icon_pos) # start extension
        self.click_and_sleep(self.qr_zoom_pos)           # bring zoom conf to front
        self.click_and_sleep(self.qr_share_pos)          # share(upload) QR image

        # search bar
        # won't copy if non selected, so write meaningless text and copy everything then slice.
        self.click_and_sleep(self.chrome_link_pos)
        pyautogui.press('home')
        pyautogui.write(self.prefix_text)
        self.link = self.copy_clipboard()[len(self.prefix_text):]

        # close chrome
        self.click_and_sleep(self.chrome_exit_button_pos)

    def send_email(self):
        'send email with SMTP'
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, GMAIL_APP_PASSWORD)

        msg = MIMEText(self.link)
        msg['Subject'] = f'출석 링크 {datetime.now().strftime(r"%Y-%m-%d %H:%M")}'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        smtp.quit()
    
    def run(self):
        try: 
            while True:
                self.get_link()
                if not self.link:
                    print('No QR: Nothing to send')
                    time.sleep(300)
                    continue
                self.send_email()
        except KeyboardInterrupt:
            print('Interrupted')

if __name__ == '__main__':
    program = SendEmail()
    program.run()
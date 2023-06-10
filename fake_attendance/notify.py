'''
Notify upon successfully reading QR
'''

import os
import sys

import smtplib
from email.mime.text import MIMEText

from datetime import datetime

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.info import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    SMTP_HOST, SMTP_PORT)
# pylint: enable=wrong-import-position

class SendEmail:
    'A class for sending email on successful QR recognization'

    def __init__(self):
        'initialize'
        self.link = ''
        self.result = ''
        self.body = ''

    def get_link(self, link):
        'get link from fake_check_in'
        self.link = link

    def get_result(self, result):
        'get result from fake_check_in'
        self.result = result

    def write_body(self):
        'write email body'
        body = f'''
        QR 코드 링크: {self.link}
        결과: {self.result}

        credit: yjmd2222's fake-attendance project https://github.com/yjmd2222/fake-attendance
        '''
        self.body = body

    def send_email(self):
        'send email'
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        msg = MIMEText(self.body)
        msg['Subject'] = f'!!fake-attendance {datetime.now().strftime(r"%Y-%m-%d %H:%M")}!!'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print('이메일 발송 성공')

        smtp.quit()

if __name__ == '__main__':
    SendEmail().send_email()

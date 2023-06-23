'''
Notify upon successfully reading QR
'''

import os
import sys

import smtplib
from smtplib import SMTPAuthenticationError
from email.mime.text import MIMEText

from datetime import datetime

from socket import gaierror

from textwrap import dedent

sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import print_with_time
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

    def record_link(self, link):
        'get link from FakeCheckIn'
        self.link = link

    def record_result(self, result):
        'get result from FakeCheckIn'
        self.result = result

    def write_body(self):
        'write email body'
        body = f'''
        QR 코드 링크: {self.link}
        결과: {self.result}

        credit: yjmd2222's fake-attendance project https://github.com/yjmd2222/fake-attendance
        '''
        self.body = dedent(body).strip()

    def send_email(self):
        'send email'
        try:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        except gaierror:
            print_with_time('SMTP 호스트 이름 확인 필요')
            return
        except TimeoutError:
            print_with_time('SMTP 포트 번호 확인 필요')
            return

        smtp.ehlo()
        smtp.starttls()
        try:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        except SMTPAuthenticationError:
            print_with_time('이메일 로그인 정보 확인 필요')
            return

        self.write_body()
        msg = MIMEText(self.body)
        msg['Subject'] = f'!!fake-attendance {datetime.now().strftime(r"%Y-%m-%d %H:%M")}!!'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print_with_time('이메일 발송 성공')

        smtp.quit()

if __name__ == '__main__':
    SendEmail().send_email()

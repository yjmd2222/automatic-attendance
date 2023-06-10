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
        'get link from FakeCheckIn'
        self.link = link

    def get_result(self, result):
        'get result from FakeCheckIn'
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
        try:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        except gaierror:
            print('SMTP 호스트 이름 확인 필요')
            return
        except TimeoutError:
            print('SMTP 포트 번호 확인 필요')
            return

        smtp.ehlo()
        smtp.starttls()
        try:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        except SMTPAuthenticationError:
            print('이메일 로그인 정보 확인 필요')
            return

        msg = MIMEText(self.body)
        msg['Subject'] = f'!!fake-attendance {datetime.now().strftime(r"%Y-%m-%d %H:%M")}!!'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print('이메일 발송 성공')

        smtp.quit()

if __name__ == '__main__':
    SendEmail().send_email()

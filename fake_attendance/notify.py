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
from fake_attendance.abc import BaseClass
from fake_attendance.helper import print_with_time
from fake_attendance.info import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    SMTP_HOST, SMTP_PORT)
from fake_attendance.settings import RESULT_DICTS
# pylint: enable=wrong-import-position

class Notify(BaseClass):
    'A class for sending email on successful QR recognization'

    def __init__(self, job_name='job_name'):
        'initialize'
        self.link = ''
        self.result = ''
        self.job_name = job_name
        self.body = ''
        self.print_name = '이메일 발송'
        super().__init__()

    def record_result(self, result):
        'record result'
        self.result = result

    def write_body(self):
        'write email body with result'
        # unfoiling nested dictionary: 'item1: result1\nitem2: result2'
        total_result = []
        for _, ovalue in self.result.items():
            single_result = []
            for ivalue in ovalue.values():
                single_result.append(str(ivalue))
            total_result.append(': '.join(single_result))
        result = '\n'.join(total_result)
        body = f'''
        {result}

        credit: yjmd2222's fake-attendance project https://github.com/yjmd2222/fake-attendance
        '''
        self.body = dedent(body).strip()

    def run(self):
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

        msg = MIMEText(self.body)
        msg['Subject'] = f'!!fake-attendance {self.job_name}\
            {datetime.now().strftime(r"%Y-%m-%d %H:%M")}!!'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print_with_time('이메일 발송 성공')

        smtp.quit()

# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-few-public-methods
class SendEmail:
    'A class for instantiating Notify class'

    # pylint: disable=no-member
    def instantiate(self):
        '''
        SendEmail.instantiate(self) method that defines\n
        a notify attribute with an instance of Notify\n
        and a result_dict attribute for multiple purposes
        '''
        self.notify = Notify(self.print_name)
        self.result_dict: dict = RESULT_DICTS[self.print_name]
    # pylint: enable=no-member
# pylint: enable=too-few-public-methods
# pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    Notify().run()

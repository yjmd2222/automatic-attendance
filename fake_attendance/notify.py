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

    def __init__(self, job_id='job_id'):
        'initialize'
        self.link = ''
        self.job_id = job_id
        self.print_name = '이메일 발송'
        super().__init__()

    def write_body(self, result):
        'write email body with result'
        if isinstance(result, dict):
            # unfoiling nested dictionary: 'item1: result1\nitem2: result2'
            total_result = []
            for _, ovalue in result.items():
                single_result = []
                for ivalue in ovalue.values():
                    single_result.append(str(ivalue))
                total_result.append(': '.join(single_result))
            result = '\n        '.join(total_result)
        body = f'''
        {result}

        credit: yjmd2222's fake-attendance project https://github.com/yjmd2222/fake-attendance
        '''
        return dedent(body).strip()

    def send_email(self, body):
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

        msg = MIMEText(body)
        msg['Subject'] = f'!!fake-attendance {self.job_id}\
            {datetime.now().strftime(r"%Y-%m-%d %H:%M")}!!'

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        print_with_time('이메일 발송 성공')

        smtp.quit()

    def run(self, result:dict=None):
        'run'
        # write email body
        body = self.write_body(result)
        # send email
        self.send_email(body)

class PrepareSendEmail:
    'A class for instantiating Notify class'

    # pylint: disable=attribute-defined-outside-init,no-member
    def define_attributes(self):
        '''
        PrepareSendEmail.define_attributes() that defines\n
        a notify attribute with an instance of Notify\n
        and a result_dict attribute for multiple purposes
        '''
        self.notify = Notify(self.print_name)
        self.result_dict: dict = RESULT_DICTS[self.print_name]
        self.is_send = False

    def decorator_send_email_reset(self, func):
        'decorator for sending email and resetting attributes'
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            if self.is_send:
                self.notify.run(self.result_dict)
            self.reset_attributes()
        return wrapper
    # pylint: enable=no-member

    def decorate_run(self):
        '''PrepareSendEmail.decorate_run() that decorates self.run()\n
        to send email and reset attributes'''
        self.run = self.decorator_send_email_reset(self.run)
    # pylint: enable=attribute-defined-outside-init

    def reset_attributes(self):
        'base method for resetting attributes at the end'

if __name__ == '__main__':
    Notify().run()

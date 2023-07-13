'''
parses arguments from command line
'''

import argparse

# pylint: disable=wrong-import-position
from fake_attendance.settings import VERBOSITY__INFO
# pylint: enable=wrong-import-position

parser = argparse.ArgumentParser(description='자동 출석 프로그램. -p, -t, time 중 하나만 선택')

parser.add_argument('time', type=str, nargs='*', help=r'%%H:%%M 형식으로 QR 체크 시간 입력')
parser.add_argument('-p', '--predefined', type=str,\
                    help='regular, sprint challenge, project day 1, project days 2-5 중 입력')
parser.add_argument('-t', '--textfile', type=str, help='.txt 텍스트 파일 이름 입력')
parser.add_argument('-v', '--verbosity', type=int, default=VERBOSITY__INFO, help='출력메시지 선택. 기본값 3')

args = parser.parse_args()

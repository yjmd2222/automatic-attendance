'''
parses arguments from command line
'''

import argparse

# pylint: disable=wrong-import-position
from fake_attendance.settings import ARGUMENT_MAP, VERBOSITY__INFO
# pylint: enable=wrong-import-position

parser = argparse.ArgumentParser(description='자동 출석 프로그램. -p, -t, time 중 하나만 선택')

parser.add_argument('time', type=str, nargs='*', help=r'%%H:%%M 형식으로 QR 체크 시간 입력')
parser.add_argument('-p', '--predefined', type=str,\
                    help=', '.join(ARGUMENT_MAP.keys()) + ' 중 입력')
parser.add_argument('-t', '--textfile', type=str, help='.txt 텍스트 파일 이름 입력')
parser.add_argument('-e', '--extrapolate', action='store_true',
                    help='입력한 시간 포함 주위 5분, 10분 단위로 출석 체크')
parser.add_argument('-v', '--verbosity', type=int, default=VERBOSITY__INFO, help='출력메시지 선택. 기본값 3')

parsed_args = parser.parse_args()

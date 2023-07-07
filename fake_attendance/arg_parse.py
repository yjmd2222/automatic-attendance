'''
parses arguments from command line
'''

import argparse

parser = argparse.ArgumentParser(description='자동 출석 프로그램')

parser.add_argument('time', type=str, nargs='*', help=r'%%H:%%M 형식으로 QR 체크 시간 입력')
parser.add_argument('-p', '--predefined', type=str,\
                    help='regular, sprint challenge, project day 1, project days 2-5 중 입력')
parser.add_argument('-t', '--textfile', type=str, help='.txt 텍스트 파일 이름 입력')
parser.add_argument('-v', '--verbosity', type=int, default=0, help='출력메시지 선택')

args = parser.parse_args()

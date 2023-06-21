'''
Settings
'''

import os
import sys
sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import get_file_path, get_time_sets
# pylint: enable=wrong-import-position

# Screen QR Reader download
GET_CRX_LINK = 'https://crx-downloader.com/'
SCREEN_QR_READER_WEBSTORE_LINK = \
    'https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln'

# Screen QR Reader interaction
SCREEN_QR_READER_POPUP_LINK = \
    'chrome-extension://ekoaehpknadfoaolagjfdefeopkhfhln/src/popup/popup.html'
SCREEN_QR_READER_BLANK = 'about:blank'
SCREEN_QR_READER_SOURCE = get_file_path('extension_0_1_2_0.crx')

# PyAutoGUI
# continue with download
CONTINUE_IMAGE = get_file_path('continue_with_download.png', 'images')
# start video
START_IMAGE = get_file_path('start_video.png', 'images')

# APScheduler timings
# 10:00, 11:20, 13:00, 14:30, 15:20, 17:00 normal
# 11:50, 13:00, 14:30 sprint challenge
# 11:00, 13:00, 15:30 project day 1 - ?
DIFF_MINUTE = 5
CHECK_IN_TIMES = [get_time_sets(*TIME_SET, DIFF_MINUTE) for TIME_SET in\
                  [(10,0), (10,30), (11, 0), (11,20), (13,11), (14,30), (15,20), (17,0)]]
CHECK_IN_TIMES = [TIME_SET for TIME_SETS in CHECK_IN_TIMES for TIME_SET in TIME_SETS]
ZOOM_ON_HOURS = '9,13'
ZOOM_QUIT_HOURS = '12,18'

# Zoom props
ZOOM_RESIZE_PARAMETERS_LIST = [i/10 for i in range(3,11)] # Change Zoom window size
ZOOM_AGREE_RECORDING_POPUP_CLASS = 'ZPRecordingConsentClass' # '이 회의는 호스트 또는 참가자가 기록 중입니다'
ZOOM_CLASSROOM_CLASS = 'ZPContentViewWndClass' # 'Zoom 회의'
ZOOM_LAUNCHING_CHROME_TITLE = '회의 시작 - Zoom - Chrome'

# Check-in props
LOGIN_WITH_KAKAO_BUTTON = 'login-form__button-title.css-caslt6'
ID_INPUT_BOX = 'loginKey--1'
PASSWORD_INPUT_BOX = 'password--2'
LOGIN_BUTTON = 'btn_g.highlight.submit'
AGREE = "//*[text()='동의합니다.']"
CHECK_IN = "//*[text()='출석']"
SUBMIT = "//*[text()='제출']"

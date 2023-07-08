'''
Settings
'''

import os
import sys
sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import (
    convert_to_datetime,
    get_file_path,
    extrapolate_time_sets,
    unfoil_time_sets)
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
# 11:20, 13:00, 15:20 normal
# 11:50, 13:00, 15:50 sprint challenge
# 10:25(Days 2-5) 11:00(Day 1), 13:00, 15:30 project
DIFF_MINUTE = 5
REGULAR_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(*TIME_SET, diff_minute=DIFF_MINUTE)\
     for TIME_SET in [(11,20), (13,11), (15,20)]]
)
SC_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(*TIME_SET, diff_minute=DIFF_MINUTE)\
     for TIME_SET in [(11,50), (13,11), (15,50)]]
)
P_D1_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(*TIME_SET, diff_minute=DIFF_MINUTE)\
     for TIME_SET in [(11,0), (13,11), (15,20)]]
)
P_D2_5_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(*TIME_SET, diff_minute=DIFF_MINUTE)\
     for TIME_SET in [(10,30), (13,11), (15,20)]]
)
ARGUMENT_MAP = {
    'regular': REGULAR_CHECK_IN_TIMES,
    'sprint challenge': SC_CHECK_IN_TIMES,
    'project day 1': P_D1_CHECK_IN_TIMES,
    'project days 2-5': P_D2_5_CHECK_IN_TIMES
}
ZOOM_ON_TIMES = [convert_to_datetime(HOUR) for HOUR in (9, 13)]
ZOOM_QUIT_TIMES = [convert_to_datetime(*TIME_SET) for TIME_SET in [(12,5), (18,5)]]
SCHED_QUIT_TIMES = [convert_to_datetime(18, 10)] # conform to the format of other 'times'

# Zoom props
ZOOM_AGREE_RECORDING_POPUP_CLASS = 'ZPRecordingConsentClass' # '이 회의는 호스트 또는 참가자가 기록 중입니다'
ZOOM_CLASSROOM_CLASS = 'ZPContentViewWndClass'
ZOOM_UPDATE_POPUP_CLASS = 'ZPForceUpdateWnd' # update popup when launching Zoom
ZOOM_UPDATE_DOWNLOAD_CLASS = 'CZPUpdateWndCls'
ZOOM_UPDATE_ACTUAL_UPDATE_CLASS = 'zoom.us Installer Engine'

# Check-in props
LOGIN_WITH_KAKAO_BUTTON = 'login-form__button-title.css-caslt6'
ID_INPUT_BOX = 'loginKey--1'
PASSWORD_INPUT_BOX = 'password--2'
LOGIN_BUTTON = 'btn_g.highlight.submit'
IFRAME = 'iframe'
AGREE = "//*[text()='동의합니다.']"
CHECK_IN = "//*[text()='출석']"
SUBMIT = "//*[text()='제출']"

# Notify result dicts
FAKE_CHECK_IN_DEFAULT_RESULT_DICT = {
    'link': {
        'name': 'QR 코드 링크',
        'content': ''
    },
    'result': {
        'name': '체크인 결과',
        'content': ''
    }
}
LAUNCH_ZOOM_DEFAULT_RESULT_DICT = {
    ZOOM_UPDATE_POPUP_CLASS: {
        'name': '줌 업데이트',
        'content': False
    },
    ZOOM_CLASSROOM_CLASS:{
        'name': '줌 회의 입장',
        'content': False
    },
    ZOOM_AGREE_RECORDING_POPUP_CLASS: {
        'name': '줌 녹화 동의',
        'content': False}
}
QUIT_ZOOM_DEFAULT_RESULT_DICT = {
    'quit': {
        'name': '줌 종료',
        'content': False
    }
}
RESULT_DICTS = {
    'QR 체크인': FAKE_CHECK_IN_DEFAULT_RESULT_DICT,
    '줌 실행': LAUNCH_ZOOM_DEFAULT_RESULT_DICT,
    '줌 종료': QUIT_ZOOM_DEFAULT_RESULT_DICT
}

# misc
INTERRUPT_SEQUENCE = 'ctrl+alt+c'
VERBOSITY__INFO = 3

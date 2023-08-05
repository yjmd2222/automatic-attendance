'''
Settings
'''

import os
import sys
from sys import platform
sys.path.append(os.getcwd())

# pylint: disable=wrong-import-position
from fake_attendance.helper import (
    convert_to_datetime,
    get_file_path,
    extrapolate_time_sets,
    unfoil_time_sets)
if platform == 'darwin':
    from fake_attendance.helper import check_appearance
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
# continue with download on win32
CONTINUE_IMAGE_WIN32 = get_file_path('continue_with_download_win32.png', 'images')
if platform == 'darwin':
    if check_appearance():
        # continue with download on darwin
        CONTINUE_IMAGE_DARWIN = get_file_path('continue_with_download_darwin_dark.png', 'images')
        # open in zoom on darwin
        OPEN_IN_ZOOM_IMAGE_DARWIN = get_file_path('open_in_zoom_darwin_dark.png', 'images')
    else:
        CONTINUE_IMAGE_DARWIN = get_file_path('continue_with_download_darwin_light.png', 'images')
        OPEN_IN_ZOOM_IMAGE_DARWIN = get_file_path('open_in_zoom_darwin_light.png', 'images')

# APScheduler timings
# 11:20, 13:00, 15:20 normal
# 11:50, 13:00, 15:50 sprint challenge
# 10:25(Days 2-5) 11:00(Day 1), 13:00, 15:30 project
# 10:50, 13:00, 15:25 section review Day 1
# 10:30, 13:00, 14:50 section review Day 2
# 11:50, 13:00, 16:50 project section
DIFF_MINUTE = 5
REGULAR_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['11:20', '13:01', '15:20']]
)
SC_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['11:50', '13:01', '15:50']]
)
P_D1_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['11:00', '13:01', '15:20']]
)
P_D2_5_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['10:30', '13:01', '15:20']]
)
SR_D1_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['10:50', '13:01', '15:25']]
)
SR_D2_CHECK_IN_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=DIFF_MINUTE)
     for TIME_ in ['10:30', '13:01', '14:50']]
)
PROJECT_TIMES = unfoil_time_sets(
    [extrapolate_time_sets(TIME_, diff_minute=3, extend_num=1)
     for TIME_ in ['12:00', '13:01', '16:50']]
)
ARGUMENT_MAP = {
    'regular': REGULAR_CHECK_IN_TIMES,
    'sprint challenge': SC_CHECK_IN_TIMES,
    'project day 1': P_D1_CHECK_IN_TIMES,
    'project days 2-5': P_D2_5_CHECK_IN_TIMES,
    'section review day 1': SR_D1_CHECK_IN_TIMES,
    'section review day 2': SR_D2_CHECK_IN_TIMES,
    'project section': PROJECT_TIMES
}
ZOOM_ON_TIMES = [convert_to_datetime(TIME_) for TIME_ in ['8:59', '12:59']]
ZOOM_QUIT_TIMES = [convert_to_datetime(TIME_) for TIME_ in ['12:05', '18:05']]
SCHED_QUIT_TIMES = [convert_to_datetime('18:10')] # conform to the format of other 'times'

# Zoom props
# win32
ZOOM_AGREE_RECORDING_POPUP_CLASS = 'ZPRecordingConsentClass' # '이 회의는 호스트 또는 참가자가 기록 중입니다'
ZOOM_UPDATE_POPUP_CLASS = 'ZPForceUpdateWnd' # update popup when launching Zoom
ZOOM_UPDATE_DOWNLOAD_CLASS = 'CZPUpdateWndCls'
ZOOM_UPDATE_ACTUAL_UPDATE_CLASS = 'zoom.us Installer Engine'
ZOOM_CLASSROOM_CLASS = 'ZPContentViewWndClass'
# darwin
ZOOM_APPLICATION_NAME = 'zoom.us'
ZOOM_AGREE_RECORDING_POPUP_NAME = '이 회의는 기록되고 있습니다'
ZOOM_UPDATE_POPUP_NAME = 'UNKNOWN0'
ZOOM_UPDATE_DOWNLOAD_NAME = 'UNKNOWN1'
ZOOM_UPDATE_ACTUAL_UPDATE_NAME = 'UNKNOWN2'
ZOOM_CLASSROOM_NAME = 'Zoom 회의' # same name used for Screen QR Reader. See fake_check_in.py

# Check-in props
LOGIN_WITH_KAKAO_BUTTON = 'login-form__button-title.css-caslt6'
ID_INPUT_BOX = 'loginId--1'
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
    '줌 업데이트': {
        'name': '줌 업데이트',
        'content': False
    },
    '줌 회의 입장':{
        'name': '줌 회의 입장',
        'content': False
    },
    '줌 녹화 동의': {
        'name': '줌 녹화 동의',
        'content': False}
}
LAUNCH_ZOOM_KEY_MAPPER = {
    ZOOM_UPDATE_POPUP_CLASS: '줌 업데이트',
    ZOOM_UPDATE_POPUP_NAME: '줌 업데이트',
    ZOOM_CLASSROOM_CLASS: '줌 회의 입장',
    ZOOM_CLASSROOM_NAME: '줌 회의 입장',
    ZOOM_AGREE_RECORDING_POPUP_CLASS: '줌 녹화 동의',
    ZOOM_AGREE_RECORDING_POPUP_NAME: '줌 녹화 동의'
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
if platform == 'win32':
    LAUNCH_ZOOM_SEQUENCE = '<ctrl>+<alt>+l'
    CHECK_IN_SEQUENCE = '<ctrl>+<alt>+c'
    QUIT_ZOOM_SEQUENCE = '<ctrl>+<alt>+q'
    QUIT_SCHED_SEQUENCE = '<ctrl>+<alt>+e'
else:
    LAUNCH_ZOOM_SEQUENCE = '<ctrl>+<cmd>+l'
    CHECK_IN_SEQUENCE = '<ctrl>+<cmd>+c'
    QUIT_ZOOM_SEQUENCE = '<ctrl>+<cmd>+q'
    QUIT_SCHED_SEQUENCE = '<ctrl>+<cmd>+e'
SEQUENCE_MAP = {
    '줌 실행': LAUNCH_ZOOM_SEQUENCE,
    'QR 체크인': CHECK_IN_SEQUENCE,
    '줌 종료': QUIT_ZOOM_SEQUENCE,
    '스케줄러 종료': QUIT_SCHED_SEQUENCE
}
VERBOSITY__INFO = 3

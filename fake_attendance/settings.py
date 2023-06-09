'''
Settings
'''

from fake_attendance.helper import get_file_path

# Screen QR Reader interaction
SCREEN_QR_READER_POPUP_LINK = \
    'chrome-extension://ekoaehpknadfoaolagjfdefeopkhfhln/src/popup/popup.html'
SCREEN_QR_READER_SOURCE = get_file_path('extension_0_1_2_0.crx')

# Screen QR Reader download
GET_CRX_LINK = 'https://crx-downloader.com/'
SCREEN_QR_READER_WEBSTORE_LINK = \
    'https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln'
# SCREEN_QR_READER_SOURCE_PATH = get_file_path('extension_0_1_2_0.crx')

# PyAutoGUI
# continue with download
CONTINUE_IMAGE = get_file_path('continue_with_download.png', 'images')
# start video
START_IMAGE = get_file_path('start_video.png', 'images')
CONFERENCE_NAME = 'Zoom 회의'

# APScheduler timings
# 10:00, 11:20, 13:00, 14:30, 15:20, 17:00 if I got them all
MINUTES = 7 # every 7 minutes
ZOOM_ON_HOUR = 12    # at hour 12
ZOOM_ON_MINUTE = 59  # at minute 55

# misc
ZOOM_RESIZE_PARAMETERS_LIST = [ # Reduce Zoom window size
    (0, 0, 1000, 800),
    (0, 0, 1600, 900),
    (0, 0, 1920, 1080)
    ]

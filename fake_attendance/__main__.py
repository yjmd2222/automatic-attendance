'''
main file
'''

import sys

from fake_attendance.download_ext import DownloadExtensionSource
from fake_attendance.scheduler import MyScheduler

if __name__ == '__main__':
    scheduler = MyScheduler()
    download = DownloadExtensionSource(scheduler)

    download.run()
    scheduler.run()
    print('right before sys.exit()')
    sys.exit()

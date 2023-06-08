'''
main file
'''

from fake_attendance.download_ext import DownloadExtensionSource
from fake_attendance.scheduler import MyScheduler

if __name__ == '__main__':
    download = DownloadExtensionSource()
    scheduler = MyScheduler()

    download.run()
    scheduler.run()

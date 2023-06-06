'''
Script to automatically send link information in QR image on a Zoom meeting every five minutes
'''

from download_ext import DownloadExtensionSource
from scheduler import MyScheduler

if __name__ == '__main__':
    download = DownloadExtensionSource()
    scheduler = MyScheduler()

    download.run()
    scheduler.run()
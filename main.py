'''
main file
'''

from download_ext import DownloadExtensionSource
from scheduler import MyScheduler

if __name__ == '__main__':
    download = DownloadExtensionSource()
    scheduler = MyScheduler()

    download.run()
    scheduler.run()

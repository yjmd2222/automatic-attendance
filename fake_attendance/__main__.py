'''
main file
'''

from fake_attendance.download_ext import DownloadExtensionSource
from fake_attendance.scheduler import MyScheduler

if __name__ == '__main__':
    # pylint: disable=ungrouped-imports
    from fake_attendance.helper import fix_pyautogui
    fix_pyautogui()
    # pylint: enable=ungrouped-imports

    scheduler = MyScheduler()
    download = DownloadExtensionSource(scheduler)

    download.run()
    scheduler.run()
